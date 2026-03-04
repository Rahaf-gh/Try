# InSpectra: System Requirements & Design Specification

---

## 1. Project Overview

**InSpectra** is an automated Electroluminescence (EL) inspection system for Photovoltaic (PV) solar panels.  

The system provides factories with a fully automated pipeline to:

- Detect defects  
- Estimate panel lifespan  
- Generate maintenance reports  

---

## 2. System Architecture (N-Tier)

The project follows a modular **N-tier architecture** to ensure scalability, maintainability, and security.

### 2.1 Presentation Tier
- UI built with **HTML, CSS, JavaScript**
- Based on refactored **Figma/Anima exports**

### 2.2 Logic Tier
- **Python (Flask)** backend
- Handles:
  - Authentication
  - Image validation
  - Workflow control
  - Results preparation

### 2.3 Data Tier
- **PostgreSQL database**
- Stores:
  - Users
  - Images
  - Inspection records
  - Reports

---

## 3. Database Schema

The database must maintain integrity across the following entities:

### 3.1 Admin
- **Primary Key:** `AdminID`
- **Attributes:** `AdminName`, `AdminEmail`, `PasswordHash`
- **Constraints:** `AdminEmail` must be **Unique**

### 3.2 Inspector
- **Primary Key:** `InspectorID`
- **Attributes:** `InspectorName`, `InspectorEmail`, `PasswordHash`
- **Constraints:** `InspectorEmail` must be **Unique`

### 3.3 Panel
- **Primary Key:** `PanelID`
- **Attributes:** `CellCount`, `CurrentValue`, `PanelSize`
- **Constraints:** `CellCount` NOT NULL

### 3.4 Image
- **Primary Key:** `ImageID`
- **Attributes:** `CaptureDate`, `ImageURL`, `PanelID` (FK)
- **Constraints:** `CaptureDate` NOT NULL

### 3.5 Defect
- **Primary Key:** `DefectID`
- **Attributes:** `DefectType`, `CellLocation`, `RiskLevel`, `ImageID` (FK)
- **Constraints:** `RiskLevel` NOT NULL

### 3.6 Report
- **Primary Key:** `ReportID`
- **Attributes:** `SeverityScore`, `DefectedCellCount`, `LifespanEstimate`
- **Constraints:** `SeverityScore` is FLOAT

---

## 4. Functional Specifications

---

### 4.1 Common & Authentication

#### Secure Login
- Authenticate using UserID and Password
- Role-based redirection (Admin vs Inspector)

#### Password Recovery
- OTP-based reset via registered email

#### Dashboard
Display real-time analytics:
- Total inspected panels
- Defect types distribution
- Technician activity

#### History
- Paginated view of past inspections
- Includes:
  - Date/Time
  - Thumbnail
  - Report link

---

### 4.2 Inspector Workflow (New Inspection)

#### Upload
- Accept EL images in:
  - JPG
  - PNG

#### Validation
- Verify:
  - File format
  - File size limits

#### Processing
- Trigger background defect analysis
- Identify:
  - Defect types
  - Risk levels
  - Lifespan estimate

#### Reporting
- Generate downloadable:
  - PDF report
  - JSON report

---

### 4.3 Admin Workflow (User Management)

#### CRUD Operations
Admin can:
- Add Inspector
- Edit Inspector
- Delete Inspector

#### RBAC
- Enforce Role-Based Access Control
- Restrict system management to authorized users only

---

## 5. Non-Functional Requirements

### Performance
- Near real-time EL image classification

### Reliability
- High precision in defect detection
- Minimal false positives

### Usability
- Consistent UI design
- Reduce short-term memory load

### Security
- Secure password hashing
- Protected internal communication
- Data integrity safeguards

---

## 6. Development Checklist for Cascade

- [ ] Set up Flask project structure with `/static` and `/templates`
- [ ] Configure SQLAlchemy models based on Section 3
- [ ] Refactor Figma/Anima HTML exports into Jinja2 templates
- [ ] Implement role-based decorators for route protection
- [ ] Integrate image upload and validation logic
- [ ] Build dashboard visualizations using database metrics
- [ ] File Upload: Implement upload handler using validation logic from Section 7.3.
- [ ] Session Security: Implement login/logout flow described in Section 7.1.
- [ ] Report Engine: Build PDF generation logic to support the "Export" functionality.

---
# 7. Logic Tier: Component Pseudocode

This section defines the procedural logic for core system functions.

---

## 7.1 Common Functions

### Login Logic

**Input:** `userID`, `password`

1. If `userID` and `password` are NOT empty:
   - Validate credentials against the `Users` table.
   - If valid:
     - Create session.
     - Redirect to Home/Dashboard.
   - Else:
     - Display: **"Invalid Username/User ID or Password"**
2. Else:
   - Display: **"Fill in the required fields"**

---

### View Dashboard

1. Check if user is logged in.
2. Fetch summary metrics:
   - Total inspections
   - Risk distribution
   - Defect counts
3. Display analytical visualizations and summary cards.

---

### View History

1. Fetch inspection records for the logged-in user.
2. Order records by `DateTime DESC`.
3. Display list including:
   - Inspection date
   - Thumbnail image
   - "View Report" button

---

### Export Inspection Report

1. Select inspection record.
2. Verify record exists.
3. Retrieve stored report data.
4. On user selecting **"Export"**:
   - Generate file (PDF or JSON).
   - Download to local disk.

---

## 7.2 Admin Functions

### Add Inspector

**Input:** `name`, `email`, `password`, `confirmPassword`

1. Verify all fields are filled.
2. Check email is unique.
3. Confirm `password == confirmPassword`.
4. Insert new record into `Users` table with role = `"Inspector"`.

---

### Delete Inspector

1. Admin selects account.
2. Confirm deletion.
3. Remove record from `Users` table.

---

### Edit Inspector

1. Admin selects account.
2. Allow updates to:
   - Name
   - Email
   - Status
3. Validate updated input.
4. Save changes to database.

---

## 7.3 User (Inspector) Functions

### New Inspection Pipeline

1. Upload EL image file.
2. Validate:
   - Format is JPG or PNG
   - File size within allowed limits

3. Preprocess:
   - Resize image
   - Normalize pixel values

4. Analyze:
   - Execute defect detection
   - Identify:
     - Defect types
     - Risk levels
     - Lifespan estimate

5. Save:
   - Store inspection record in database
   - Store detected defects
   - Store generated report data

6. Display:
   - Show annotated EL image
   - Display results panel with metrics

---

