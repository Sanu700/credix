package com.debtforge.dto;

import com.debtforge.model.Transaction;
import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class PaymentRequest {

    @NotNull @DecimalMin(value = "1.0")
    private BigDecimal amount;

    private LocalDate paymentDate;

    private Transaction.TransactionType type;

    private String remarks;
}
