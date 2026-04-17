package com.debtforge.dto;

import lombok.Builder;
import lombok.Data;
import java.math.BigDecimal;

@Data
@Builder
public class EmiResponse {
    private Long loanId;
    private BigDecimal principal;
    private BigDecimal annualInterestRate;
    private Integer tenureMonths;
    private BigDecimal monthlyEmi;
    private BigDecimal totalPayable;
    private BigDecimal totalInterest;
}
