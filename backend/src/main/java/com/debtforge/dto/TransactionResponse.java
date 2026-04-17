package com.debtforge.dto;

import com.debtforge.model.Transaction;
import lombok.Builder;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@Builder
public class TransactionResponse {
    private Long id;
    private BigDecimal amount;
    private LocalDate paymentDate;
    private Transaction.TransactionType type;
    private String remarks;
}
