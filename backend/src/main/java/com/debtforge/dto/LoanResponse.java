package com.debtforge.dto;

import com.debtforge.model.Loan;
import lombok.Builder;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
@Builder
public class LoanResponse {
    private Long id;
    private String borrowerName;
    private BigDecimal principal;
    private BigDecimal annualInterestRate;
    private Integer tenureMonths;
    private LocalDate startDate;
    private Loan.LoanStatus status;
    private BigDecimal totalAmountPaid;
    private BigDecimal emi;
    private BigDecimal outstandingBalance;
    private List<TransactionResponse> transactions;
}
