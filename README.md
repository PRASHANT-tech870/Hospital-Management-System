
# Hospital Management System (HMS) 🏥

A modern, full-stack Hospital Management System built with FastAPI and SQLite, featuring a professional UI for managing hospital operations efficiently. The system provides dedicated portals for patients, doctors, staff, and administrators.

## Features 🌟

### Multi-User System
- **Patient Portal**
  - Schedule and manage appointments
  - View medical history and doctor notes
  - Track appointments status
  - Access billing information
  - Update personal information

- **Doctor Dashboard**
  - Manage patient appointments
  - Access patient medical histories
  - Write and manage medical notes
  - Set weekly availability schedule
  - Use AI-powered diagnostic tools
  - Track patient progress

- **Staff Portal**
  - View assigned patients
  - Access patient details
  - Update patient records
  - Manage patient assignments
  - Track patient status

- **Admin Dashboard**
  - Comprehensive user management
  - Department administration
  - Equipment inventory tracking
  - Staff-patient assignments
  - System monitoring and maintenance
  - Resource allocation

### Core Features 💡
1. **Appointment Management**
   - Real-time scheduling
   - Automated time slot generation
   - Status tracking (Scheduled/Confirmed/Completed/Cancelled)
   - Conflict prevention

2. **Medical Records**
   - Comprehensive patient history
   - Doctor notes and observations
   - Treatment tracking
   - Chronic condition monitoring

3. **Billing System**
   - Automated invoice generation
   - Payment tracking
   - Consultation fee management
   - Invoice item categorization

4. **Equipment Management**
   - Inventory tracking
   - Maintenance scheduling
   - Status monitoring
   - Department allocation

5. **Department Management**
   - Budget tracking
   - Staff allocation
   - Resource management
   - Performance monitoring

## Technical Stack 🛠

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database system
- **Pydantic**: Data validation using Python type annotations
- **Python 3.8+**: Core programming language

### Frontend
- **HTML5/CSS3**: Modern, responsive layouts
- **JavaScript**: Dynamic client-side functionality
- **Custom CSS Framework**: Professional UI components
- **Material Icons**: Visual elements and icons

## Installation and Setup 📦

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hospital-management-system.git
cd hospital-management-system
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
python -m app.db
```

5. **Start the server**
```bash
uvicorn app.main:app --reload
```

## Project Structure 📁
```
hospital-management-system/
├── app/
│   ├── static/              # Frontend assets
│   │   ├── doctor-dashboard.html
│   │   ├── patient-dashboard.html
│   │   ├── staff-dashboard.html
│   │   ├── shared-dashboard.css
│   │   └── style.css
│   ├── routers/            # API endpoints
│   │   ├── admin.py
│   │   ├── appointments.py
│   │   ├── billing.py
│   │   ├── doctors.py
│   │   ├── medical_history.py
│   │   └── patients.py
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── utils/             # Utility functions
│   ├── main.py            # Application entry
│   └── db.py              # Database configuration
├── requirements.txt
└── README.md
```

## API Documentation 📚

### Authentication
- `POST /api/login`: User authentication
- `POST /api/register`: New user registration
- `POST /api/admin/login`: Admin authentication

### Patient Management
- `GET /api/patients/{id}`: Retrieve patient details
- `GET /api/patients/{id}/appointments`: Get patient appointments
- `GET /api/patients/{id}/medical-history`: Access medical history
- `POST /api/patients/`: Create new patient
- `PUT /api/patients/{id}`: Update patient information

### Doctor Operations
- `GET /api/doctors/schedule`: Retrieve doctor schedule
- `POST /api/doctors/schedule/update`: Update availability
- `GET /api/doctors/appointments`: Get appointments
- `GET /api/doctors/specializations`: List specializations
- `GET /api/doctors/{id}/patients`: Get doctor's patients

### Appointment Management
- `POST /api/appointments/book`: Book new appointment
- `GET /api/appointments/doctors/available`: Get available doctors
- `PUT /api/appointments/{id}/status`: Update appointment status

### Medical Records
- `POST /api/medical/history`: Add medical history
- `GET /api/medical/history/patient/{id}`: Get patient history
- `POST /api/medical/notes`: Add doctor notes
- `GET /api/medical/notes/patient/{id}`: Get patient notes

### Admin Controls
- `POST /api/admin/equipment`: Add equipment
- `GET /api/admin/equipment`: List all equipment
- `PUT /api/admin/equipment/{id}`: Update equipment
- `POST /api/admin/assign-patient`: Assign patient to staff
- `GET /api/admin/departments`: List departments

## Security Features 🔒
- Role-based access control (RBAC)
- Secure password handling
- Input validation and sanitization
- SQL injection protection
- Session management
- Error handling and logging

## Contributing 🤝
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬
For support:
- Create an issue in the repository
- Contact: support@hms.com
- Documentation: [Wiki](link-to-wiki)

## Acknowledgments 🙏
- FastAPI documentation and community
- SQLAlchemy documentation
- Modern UI/UX design principles
- Healthcare management best practices

---



