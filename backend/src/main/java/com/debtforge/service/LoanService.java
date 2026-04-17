package com.debtforge.service;

import com.debtforge.dto.*;
import com.debtforge.exception.LoanNotFoundException;
import com.debtforge.model.Loan;
import com.debtforge.model.Transaction;
import com.debtforge.repository.LoanRepository;
import com.debtforge.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class LoanService {

    private final LoanRepository loanRepository;
    private final TransactionRepository transactionRepository;

    // ── EMI Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1) ──
    public BigDecimal calculateEmi(BigDecimal principal, BigDecimal annualRate, int months) {
        if (annualRate.compareTo(BigDecimal.ZERO) == 0) {
            return principal.divide(BigDecimal.valueOf(months), 2, RoundingMode.HALF_UP);
        }
        BigDecimal monthlyRate = annualRate
                .divide(BigDecimal.valueOf(1200), 10, RoundingMode.HALF_UP);

        // (1 + r)^n
        BigDecimal onePlusR = BigDecimal.ONE.add(monthlyRate);
        BigDecimal power = onePlusR.pow(months, MathContext.DECIMAL64);

        // numerator: P * r * (1+r)^n
        BigDecimal numerator = principal.multiply(monthlyRate).multiply(power);

        // denominator: (1+r)^n - 1
        BigDecimal denominator = power.subtract(BigDecimal.ONE);

        return numerator.divide(denominator, 2, RoundingMode.HALF_UP);
    }

    @Transactional
    public LoanResponse createLoan(LoanRequest req) {
        BigDecimal emi = calculateEmi(req.getPrincipal(), req.getAnnualInterestRate(), req.getTenureMonths());

        Loan loan = Loan.builder()
                .borrowerName(req.getBorrowerName())
                .principal(req.getPrincipal())
                .annualInterestRate(req.getAnnualInterestRate())
                .tenureMonths(req.getTenureMonths())
                .startDate(req.getStartDate() != null ? req.getStartDate() : LocalDate.now())
                .status(Loan.LoanStatus.ACTIVE)
                .totalAmountPaid(BigDecimal.ZERO)
                .build();

        loan = loanRepository.save(loan);
        log.info("Created loan id={} for borrower={}", loan.getId(), loan.getBorrowerName());
        return toResponse(loan, emi, List.of());
    }

    @Transactional(readOnly = true)
    public EmiResponse getEmi(Long loanId) {
        Loan loan = findLoan(loanId);
        BigDecimal emi = calculateEmi(loan.getPrincipal(), loan.getAnnualInterestRate(), loan.getTenureMonths());
        BigDecimal totalPayable = emi.multiply(BigDecimal.valueOf(loan.getTenureMonths()));
        BigDecimal totalInterest = totalPayable.subtract(loan.getPrincipal());

        return EmiResponse.builder()
                .loanId(loanId)
                .principal(loan.getPrincipal())
                .annualInterestRate(loan.getAnnualInterestRate())
                .tenureMonths(loan.getTenureMonths())
                .monthlyEmi(emi)
                .totalPayable(totalPayable)
                .totalInterest(totalInterest)
                .build();
    }

    @Transactional
    public TransactionResponse recordPayment(Long loanId, PaymentRequest req) {
        Loan loan = findLoan(loanId);

        if (loan.getStatus() == Loan.LoanStatus.CLOSED) {
            throw new IllegalStateException("Loan id=" + loanId + " is already closed.");
        }

        Transaction tx = Transaction.builder()
                .loan(loan)
                .amount(req.getAmount())
                .paymentDate(req.getPaymentDate() != null ? req.getPaymentDate() : LocalDate.now())
                .type(req.getType() != null ? req.getType() : Transaction.TransactionType.EMI)
                .remarks(req.getRemarks())
                .build();

        tx = transactionRepository.save(tx);

        // Update totals
        loan.setTotalAmountPaid(loan.getTotalAmountPaid().add(req.getAmount()));

        // Check if loan is fully paid
        BigDecimal emi = calculateEmi(loan.getPrincipal(), loan.getAnnualInterestRate(), loan.getTenureMonths());
        BigDecimal totalPayable = emi.multiply(BigDecimal.valueOf(loan.getTenureMonths()));
        if (loan.getTotalAmountPaid().compareTo(totalPayable) >= 0) {
            loan.setStatus(Loan.LoanStatus.CLOSED);
            log.info("Loan id={} marked CLOSED - fully paid", loanId);
        }

        loanRepository.save(loan);
        return toTxResponse(tx);
    }

    @Transactional(readOnly = true)
    public LoanResponse getLoan(Long loanId) {
        Loan loan = findLoan(loanId);
        BigDecimal emi = calculateEmi(loan.getPrincipal(), loan.getAnnualInterestRate(), loan.getTenureMonths());
        List<Transaction> txList = transactionRepository.findByLoanIdOrderByPaymentDateDesc(loanId);
        List<TransactionResponse> txResponses = txList.stream().map(this::toTxResponse).collect(Collectors.toList());
        return toResponse(loan, emi, txResponses);
    }

    // ── Helpers ──────────────────────────────────────────────

    private Loan findLoan(Long id) {
        return loanRepository.findById(id).orElseThrow(() -> new LoanNotFoundException(id));
    }

    private LoanResponse toResponse(Loan loan, BigDecimal emi, List<TransactionResponse> txs) {
        BigDecimal totalPayable = emi.multiply(BigDecimal.valueOf(loan.getTenureMonths()));
        BigDecimal outstanding = totalPayable.subtract(loan.getTotalAmountPaid()).max(BigDecimal.ZERO);

        return LoanResponse.builder()
                .id(loan.getId())
                .borrowerName(loan.getBorrowerName())
                .principal(loan.getPrincipal())
                .annualInterestRate(loan.getAnnualInterestRate())
                .tenureMonths(loan.getTenureMonths())
                .startDate(loan.getStartDate())
                .status(loan.getStatus())
                .totalAmountPaid(loan.getTotalAmountPaid())
                .emi(emi)
                .outstandingBalance(outstanding)
                .transactions(txs)
                .build();
    }

    private TransactionResponse toTxResponse(Transaction tx) {
        return TransactionResponse.builder()
                .id(tx.getId())
                .amount(tx.getAmount())
                .paymentDate(tx.getPaymentDate())
                .type(tx.getType())
                .remarks(tx.getRemarks())
                .build();
    }
}
