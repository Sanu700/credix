package com.debtforge.dto;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class LoanRequest {

    @NotBlank(message = "Borrower name is required")
    private String borrowerName;

    @NotNull @DecimalMin(value = "1000.0", message = "Principal must be at least 1000")
    private BigDecimal principal;

    @NotNull @DecimalMin(value = "0.1") @DecimalMax(value = "100.0")
    private BigDecimal annualInterestRate;

    @NotNull @Min(value = 1) @Max(value = 360)
    private Integer tenureMonths;

    private LocalDate startDate;
}
