# ─────────────────────────────────────────────────────────────
# DebtForge — Build & Zip Script (PowerShell)
# Run from the PARENT folder of DebtForge\
# Usage: .\build.ps1
# ─────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"

$ROOT  = "DebtForge"
$BE    = "$ROOT\backend\src\main\java\com\debtforge"
$RES   = "$ROOT\backend\src\main\resources"
$FE    = "$ROOT\frontend"

Write-Host "📁 Creating folder structure..." -ForegroundColor Cyan
@(
  "$BE\controller", "$BE\service", "$BE\repository",
  "$BE\model", "$BE\dto", "$BE\exception", "$BE\config",
  $RES, $FE
) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

function Write-File($path, $content) {
    Set-Content -Path $path -Value $content -Encoding UTF8
}

Write-Host "✍  Writing backend files..." -ForegroundColor Cyan

# ── pom.xml ──────────────────────────────────────────────────
Write-File "$ROOT\backend\pom.xml" @'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    <groupId>com.debtforge</groupId>
    <artifactId>debtforge</artifactId>
    <version>1.0.0</version>
    <properties><java.version>17</java.version></properties>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
        <dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>runtime</scope></dependency>
        <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes><exclude><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId></exclude></excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'@

# ── application.properties ───────────────────────────────────
Write-File "$RES\application.properties" @'
server.port=8080
spring.datasource.url=jdbc:h2:mem:debtforge;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
'@

# ── DebtForgeApplication.java ────────────────────────────────
Write-File "$BE\DebtForgeApplication.java" @'
package com.debtforge;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication
public class DebtForgeApplication {
    public static void main(String[] args) { SpringApplication.run(DebtForgeApplication.class, args); }
}
'@

# ── Loan.java ────────────────────────────────────────────────
Write-File "$BE\model\Loan.java" @'
package com.debtforge.model;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal; import java.time.LocalDate; import java.util.*;
@Entity @Table(name="loans") @Data @Builder @NoArgsConstructor @AllArgsConstructor
public class Loan {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @Column(nullable=false) private String borrowerName;
    @Column(nullable=false) private BigDecimal principal;
    @Column(nullable=false) private BigDecimal annualInterestRate;
    @Column(nullable=false) private Integer tenureMonths;
    @Column(nullable=false) private LocalDate startDate;
    @Enumerated(EnumType.STRING) @Column(nullable=false) private LoanStatus status;
    @Column(nullable=false) private BigDecimal totalAmountPaid;
    @OneToMany(mappedBy="loan",cascade=CascadeType.ALL,fetch=FetchType.LAZY)
    @Builder.Default @ToString.Exclude @EqualsAndHashCode.Exclude
    private List<Transaction> transactions = new ArrayList<>();
    public enum LoanStatus { ACTIVE, CLOSED, DEFAULTED }
}
'@

# ── Transaction.java ─────────────────────────────────────────
Write-File "$BE\model\Transaction.java" @'
package com.debtforge.model;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal; import java.time.LocalDate;
@Entity @Table(name="transactions") @Data @Builder @NoArgsConstructor @AllArgsConstructor
public class Transaction {
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @ManyToOne(fetch=FetchType.LAZY) @JoinColumn(name="loan_id",nullable=false)
    @ToString.Exclude @EqualsAndHashCode.Exclude private Loan loan;
    @Column(nullable=false) private BigDecimal amount;
    @Column(nullable=false) private LocalDate paymentDate;
    @Enumerated(EnumType.STRING) @Column(nullable=false) private TransactionType type;
    private String remarks;
    public enum TransactionType { EMI, PREPAYMENT, LATE_FEE }
}
'@

# ── DTOs ─────────────────────────────────────────────────────
Write-File "$BE\dto\LoanRequest.java" @'
package com.debtforge.dto;
import jakarta.validation.constraints.*; import lombok.Data;
import java.math.BigDecimal; import java.time.LocalDate;
@Data public class LoanRequest {
    @NotBlank private String borrowerName;
    @NotNull @DecimalMin("1000.0") private BigDecimal principal;
    @NotNull @DecimalMin("0.1") @DecimalMax("100.0") private BigDecimal annualInterestRate;
    @NotNull @Min(1) @Max(360) private Integer tenureMonths;
    private LocalDate startDate;
}
'@

Write-File "$BE\dto\LoanResponse.java" @'
package com.debtforge.dto;
import com.debtforge.model.Loan; import lombok.*; import java.math.BigDecimal;
import java.time.LocalDate; import java.util.List;
@Data @Builder public class LoanResponse {
    private Long id; private String borrowerName; private BigDecimal principal;
    private BigDecimal annualInterestRate; private Integer tenureMonths;
    private LocalDate startDate; private Loan.LoanStatus status;
    private BigDecimal totalAmountPaid; private BigDecimal emi;
    private BigDecimal outstandingBalance; private List<TransactionResponse> transactions;
}
'@

Write-File "$BE\dto\EmiResponse.java" @'
package com.debtforge.dto;
import lombok.*; import java.math.BigDecimal;
@Data @Builder public class EmiResponse {
    private Long loanId; private BigDecimal principal; private BigDecimal annualInterestRate;
    private Integer tenureMonths; private BigDecimal monthlyEmi;
    private BigDecimal totalPayable; private BigDecimal totalInterest;
}
'@

Write-File "$BE\dto\PaymentRequest.java" @'
package com.debtforge.dto;
import com.debtforge.model.Transaction; import jakarta.validation.constraints.*;
import lombok.Data; import java.math.BigDecimal; import java.time.LocalDate;
@Data public class PaymentRequest {
    @NotNull @DecimalMin("1.0") private BigDecimal amount;
    private LocalDate paymentDate; private Transaction.TransactionType type; private String remarks;
}
'@

Write-File "$BE\dto\TransactionResponse.java" @'
package com.debtforge.dto;
import com.debtforge.model.Transaction; import lombok.*; import java.math.BigDecimal; import java.time.LocalDate;
@Data @Builder public class TransactionResponse {
    private Long id; private BigDecimal amount; private LocalDate paymentDate;
    private Transaction.TransactionType type; private String remarks;
}
'@

# ── Repositories ─────────────────────────────────────────────
Write-File "$BE\repository\LoanRepository.java" @'
package com.debtforge.repository;
import com.debtforge.model.Loan; import org.springframework.data.jpa.repository.JpaRepository; import org.springframework.stereotype.Repository;
@Repository public interface LoanRepository extends JpaRepository<Loan, Long> {}
'@

Write-File "$BE\repository\TransactionRepository.java" @'
package com.debtforge.repository;
import com.debtforge.model.Transaction; import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository; import java.util.List;
@Repository public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    List<Transaction> findByLoanIdOrderByPaymentDateDesc(Long loanId);
}
'@

# ── Exceptions ───────────────────────────────────────────────
Write-File "$BE\exception\LoanNotFoundException.java" @'
package com.debtforge.exception;
public class LoanNotFoundException extends RuntimeException {
    public LoanNotFoundException(Long id) { super("Loan not found with id: " + id); }
}
'@

Write-File "$BE\exception\GlobalExceptionHandler.java" @'
package com.debtforge.exception;
import org.springframework.http.*; import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException; import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime; import java.util.*;
@RestControllerAdvice public class GlobalExceptionHandler {
    record ErrorResponse(int status, String error, String message, LocalDateTime timestamp) {}
    @ExceptionHandler(LoanNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(LoanNotFoundException ex) {
        return ResponseEntity.status(404).body(new ErrorResponse(404,"Not Found",ex.getMessage(),LocalDateTime.now())); }
    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<ErrorResponse> handleIllegal(IllegalStateException ex) {
        return ResponseEntity.status(400).body(new ErrorResponse(400,"Bad Request",ex.getMessage(),LocalDateTime.now())); }
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String,Object>> handleValidation(MethodArgumentNotValidException ex) {
        Map<String,String> errs = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(e->errs.put(((FieldError)e).getField(),e.getDefaultMessage()));
        return ResponseEntity.badRequest().body(Map.of("status",400,"error","Validation Failed","fields",errs,"timestamp",LocalDateTime.now())); }
}
'@

# ── Config ───────────────────────────────────────────────────
Write-File "$BE\config\WebConfig.java" @'
package com.debtforge.config;
import org.springframework.context.annotation.Configuration; import org.springframework.web.servlet.config.annotation.*;
@Configuration public class WebConfig implements WebMvcConfigurer {
    @Override public void addCorsMappings(CorsRegistry r) {
        r.addMapping("/**").allowedOrigins("*").allowedMethods("GET","POST","PUT","DELETE","OPTIONS").allowedHeaders("*"); }
}
'@

# ── Service ──────────────────────────────────────────────────
Write-File "$BE\service\LoanService.java" @'
package com.debtforge.service;
import com.debtforge.dto.*; import com.debtforge.exception.LoanNotFoundException;
import com.debtforge.model.*; import com.debtforge.repository.*;
import lombok.RequiredArgsConstructor; import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal; import java.math.MathContext; import java.math.RoundingMode;
import java.time.LocalDate; import java.util.List; import java.util.stream.Collectors;
@Service @RequiredArgsConstructor public class LoanService {
    private final LoanRepository loanRepository;
    private final TransactionRepository transactionRepository;
    public BigDecimal calculateEmi(BigDecimal principal, BigDecimal annualRate, int months) {
        if (annualRate.compareTo(BigDecimal.ZERO)==0)
            return principal.divide(BigDecimal.valueOf(months),2,RoundingMode.HALF_UP);
        BigDecimal r = annualRate.divide(BigDecimal.valueOf(1200),10,RoundingMode.HALF_UP);
        BigDecimal pow = r.add(BigDecimal.ONE).pow(months,MathContext.DECIMAL64);
        return principal.multiply(r).multiply(pow).divide(pow.subtract(BigDecimal.ONE),2,RoundingMode.HALF_UP);
    }
    @Transactional public LoanResponse createLoan(LoanRequest req) {
        BigDecimal emi = calculateEmi(req.getPrincipal(),req.getAnnualInterestRate(),req.getTenureMonths());
        Loan loan = Loan.builder().borrowerName(req.getBorrowerName()).principal(req.getPrincipal())
            .annualInterestRate(req.getAnnualInterestRate()).tenureMonths(req.getTenureMonths())
            .startDate(req.getStartDate()!=null?req.getStartDate():LocalDate.now())
            .status(Loan.LoanStatus.ACTIVE).totalAmountPaid(BigDecimal.ZERO).build();
        return toResponse(loanRepository.save(loan),emi,List.of());
    }
    @Transactional(readOnly=true) public EmiResponse getEmi(Long id) {
        Loan l = findLoan(id);
        BigDecimal emi = calculateEmi(l.getPrincipal(),l.getAnnualInterestRate(),l.getTenureMonths());
        BigDecimal total = emi.multiply(BigDecimal.valueOf(l.getTenureMonths()));
        return EmiResponse.builder().loanId(id).principal(l.getPrincipal())
            .annualInterestRate(l.getAnnualInterestRate()).tenureMonths(l.getTenureMonths())
            .monthlyEmi(emi).totalPayable(total).totalInterest(total.subtract(l.getPrincipal())).build();
    }
    @Transactional public TransactionResponse recordPayment(Long id, PaymentRequest req) {
        Loan l = findLoan(id);
        if (l.getStatus()==Loan.LoanStatus.CLOSED) throw new IllegalStateException("Loan "+id+" is already closed.");
        Transaction tx = Transaction.builder().loan(l).amount(req.getAmount())
            .paymentDate(req.getPaymentDate()!=null?req.getPaymentDate():LocalDate.now())
            .type(req.getType()!=null?req.getType():Transaction.TransactionType.EMI)
            .remarks(req.getRemarks()).build();
        tx = transactionRepository.save(tx);
        l.setTotalAmountPaid(l.getTotalAmountPaid().add(req.getAmount()));
        BigDecimal totalPayable = calculateEmi(l.getPrincipal(),l.getAnnualInterestRate(),l.getTenureMonths())
            .multiply(BigDecimal.valueOf(l.getTenureMonths()));
        if (l.getTotalAmountPaid().compareTo(totalPayable)>=0) l.setStatus(Loan.LoanStatus.CLOSED);
        loanRepository.save(l);
        return toTxResponse(tx);
    }
    @Transactional(readOnly=true) public LoanResponse getLoan(Long id) {
        Loan l = findLoan(id);
        BigDecimal emi = calculateEmi(l.getPrincipal(),l.getAnnualInterestRate(),l.getTenureMonths());
        List<TransactionResponse> txs = transactionRepository.findByLoanIdOrderByPaymentDateDesc(id)
            .stream().map(this::toTxResponse).collect(Collectors.toList());
        return toResponse(l,emi,txs);
    }
    private Loan findLoan(Long id) { return loanRepository.findById(id).orElseThrow(()->new LoanNotFoundException(id)); }
    private LoanResponse toResponse(Loan l, BigDecimal emi, List<TransactionResponse> txs) {
        BigDecimal total = emi.multiply(BigDecimal.valueOf(l.getTenureMonths()));
        return LoanResponse.builder().id(l.getId()).borrowerName(l.getBorrowerName()).principal(l.getPrincipal())
            .annualInterestRate(l.getAnnualInterestRate()).tenureMonths(l.getTenureMonths())
            .startDate(l.getStartDate()).status(l.getStatus()).totalAmountPaid(l.getTotalAmountPaid())
            .emi(emi).outstandingBalance(total.subtract(l.getTotalAmountPaid()).max(BigDecimal.ZERO))
            .transactions(txs).build();
    }
    private TransactionResponse toTxResponse(Transaction t) {
        return TransactionResponse.builder().id(t.getId()).amount(t.getAmount())
            .paymentDate(t.getPaymentDate()).type(t.getType()).remarks(t.getRemarks()).build();
    }
}
'@

# ── Controller ───────────────────────────────────────────────
Write-File "$BE\controller\LoanController.java" @'
package com.debtforge.controller;
import com.debtforge.dto.*; import com.debtforge.service.LoanService;
import jakarta.validation.Valid; import lombok.RequiredArgsConstructor;
import org.springframework.http.*; import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/loan") @RequiredArgsConstructor @CrossOrigin(origins="*")
public class LoanController {
    private final LoanService loanService;
    @PostMapping public ResponseEntity<LoanResponse> createLoan(@Valid @RequestBody LoanRequest r) {
        return ResponseEntity.status(HttpStatus.CREATED).body(loanService.createLoan(r)); }
    @GetMapping("/{id}") public ResponseEntity<LoanResponse> getLoan(@PathVariable Long id) {
        return ResponseEntity.ok(loanService.getLoan(id)); }
    @GetMapping("/{id}/emi") public ResponseEntity<EmiResponse> getEmi(@PathVariable Long id) {
        return ResponseEntity.ok(loanService.getEmi(id)); }
    @PostMapping("/{id}/payment") public ResponseEntity<TransactionResponse> pay(
        @PathVariable Long id, @Valid @RequestBody PaymentRequest r) {
        return ResponseEntity.status(HttpStatus.CREATED).body(loanService.recordPayment(id,r)); }
}
'@

Write-Host "✍  Writing frontend files..." -ForegroundColor Cyan

Write-File "$FE\requirements.txt" @'
streamlit>=1.32.0
requests>=2.31.0
pandas>=2.0.0
'@

Write-Host "  [INFO] app.py must be placed in $FE\ (use provided app.py)" -ForegroundColor Yellow

Write-File "$ROOT\README.md" @'
# DebtForge
## Backend
cd backend && mvn spring-boot:run
## Frontend
cd frontend && pip install -r requirements.txt && streamlit run app.py
'@

Write-Host ""
Write-Host "🗜  Zipping project..." -ForegroundColor Cyan
Compress-Archive -Path "$ROOT\*" -DestinationPath "DebtForge.zip" -Force

Write-Host ""
Write-Host "✅ Done! DebtForge.zip created." -ForegroundColor Green
Write-Host "   Backend  → cd DebtForge\backend && mvn spring-boot:run"
Write-Host "   Frontend → cd DebtForge\frontend && pip install -r requirements.txt && streamlit run app.py"
