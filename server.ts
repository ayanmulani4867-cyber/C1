import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { createProxyMiddleware } from "http-proxy-middleware";

async function startServer() {
  const app = express();
  const PORT = Number(process.env.PORT) || 3000;
  const FLASK_PORT = process.env.FLASK_PORT || "5000";
  const FLASK_URL = process.env.FLASK_URL || `http://127.0.0.1:${FLASK_PORT}`;

  // Proxy /api and /static/uploads requests to the Flask backend without stripping prefixes
  app.use(
    createProxyMiddleware({
      filter: (pathname, req) => pathname.startsWith("/api") || pathname.startsWith("/static/uploads"),
      target: FLASK_URL,
      changeOrigin: true,
      ws: true,
    })
  );

  app.use(express.json());

  // Health endpoint
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", app: "Campus Connect ERP", time: new Date().toISOString() });
  });

  // Admin Faculty Registration API
  app.post("/api/admin/faculty", async (req, res) => {
    try {
      const data = req.body || {};
      const firstName = (data.firstName || data.first_name || '').toString().trim();
      const lastName = (data.lastName || data.last_name || '').toString().trim();
      const officialEmail = (data.officialEmail || data.official_email || '').toString().trim().toLowerCase();
      const mobile = (data.mobile || data.phone || '').toString().trim();

      if (!firstName || !lastName) {
        return res.status(400).json({
          success: false,
          error: "First name and last name are required.",
          message: "First name and last name are required."
        });
      }

      if (!officialEmail) {
        return res.status(400).json({
          success: false,
          error: "Official email is required.",
          message: "Official email is required."
        });
      }

      if (!mobile || mobile.replace(/\D/g, '').length < 10) {
        return res.status(400).json({
          success: false,
          error: "A valid 10-15 digit mobile number is required.",
          message: "A valid 10-15 digit mobile number is required."
        });
      }

      // Generate IDs
      const currentYear = new Date().getFullYear();
      const randSuffix = Math.floor(1000 + Math.random() * 9000);
      const generatedEmpId = data.employeeId || data.employee_id || `EMP${currentYear}${randSuffix}`;
      const generatedFacId = data.facultyId || data.faculty_id || `FAC-${(data.departmentId || 'CSE').replace('dept-', '').toUpperCase()}-${randSuffix}`;
      const fullName = `Prof. ${firstName} ${lastName}`;
      const isHod = (data.designation || '').toString().toUpperCase().includes('HOD') || (data.designation || '').toString().toUpperCase().includes('HEAD');

      const generatedUserId = `u-${Date.now()}`;
      const facultyRecord = {
        id: `fac-${Date.now()}`,
        user_id: generatedUserId,
        userId: generatedUserId,
        faculty_id: generatedFacId,
        facultyId: generatedFacId,
        employee_id: generatedEmpId,
        employeeId: generatedEmpId,
        first_name: firstName,
        firstName: firstName,
        last_name: lastName,
        lastName: lastName,
        full_name: fullName,
        fullName: fullName,
        official_email: officialEmail,
        officialEmail: officialEmail,
        personal_email: data.personalEmail || data.personal_email || `${firstName.toLowerCase()}@gmail.com`,
        personalEmail: data.personalEmail || data.personal_email || `${firstName.toLowerCase()}@gmail.com`,
        mobile: mobile,
        phone: mobile,
        department_id: data.departmentId || data.department_id || 'dept-cse',
        departmentId: data.departmentId || data.department_id || 'dept-cse',
        designation: data.designation || 'Assistant Professor',
        employment_type: data.employmentType || data.employment_type || 'Permanent',
        employmentType: data.employmentType || data.employment_type || 'Permanent',
        qualification: data.qualification || 'Ph.D. in Computer Science',
        specialization: data.specialization || 'Artificial Intelligence',
        experience_years: Number(data.experienceYears || data.experience_years) || 0,
        experienceYears: Number(data.experienceYears || data.experience_years) || 0,
        status: data.status || 'Active',
        room_office: data.roomOffice || data.room_office || 'Cabin 304',
        roomOffice: data.roomOffice || data.room_office || 'Cabin 304',
        photo: data.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
      };

      const credentials = {
        username: officialEmail,
        login_id: officialEmail,
        employee_id: generatedEmpId,
        faculty_id: generatedFacId,
        role: isHod ? 'HOD' : 'FACULTY',
        initial_password: mobile,
        must_change_password: true,
      };

      return res.status(201).json({
        success: true,
        message: `Faculty member ${fullName} registered successfully! Auto-generated Employee ID: ${generatedEmpId}. Login email: ${officialEmail}.`,
        faculty: facultyRecord,
        credentials: credentials,
      });
    } catch (err: any) {
      return res.status(500).json({
        success: false,
        error: err.message || "Internal server error registering faculty member.",
        message: err.message || "Internal server error registering faculty member."
      });
    }
  });

  // Admin Student Registration API
  app.post(["/api/admin/students", "/api/admin/student"], async (req, res) => {
    try {
      const data = req.body || {};
      const firstName = (data.firstName || data.first_name || '').toString().trim();
      const lastName = (data.lastName || data.last_name || '').toString().trim();
      const collegeEmail = (data.collegeEmail || data.college_email || data.email || '').toString().trim().toLowerCase();
      const mobile = (data.mobile || data.phone || '').toString().trim();

      if (!firstName || !lastName) {
        return res.status(400).json({
          success: false,
          error: "First name and last name are required.",
          message: "First name and last name are required."
        });
      }

      if (!collegeEmail) {
        return res.status(400).json({
          success: false,
          error: "College email is required.",
          message: "College email is required."
        });
      }

      if (!mobile || mobile.replace(/\D/g, '').length < 10) {
        return res.status(400).json({
          success: false,
          error: "A valid 10-15 digit mobile number is required.",
          message: "A valid 10-15 digit mobile number is required."
        });
      }

      const currentYear = new Date().getFullYear();
      const randSuffix = Math.floor(1000 + Math.random() * 9000);
      const studentId = data.studentId || data.student_id || `STU-${currentYear}-${randSuffix}`;
      const admissionNo = data.admissionNo || data.admission_no || `ADM-${currentYear}-${randSuffix}`;
      const enrollmentNo = data.enrollmentNo || data.enrollment_no || `EN${currentYear}CSE${randSuffix}`;
      const rollNo = data.rollNo || data.roll_no || `${String(currentYear).slice(-2)}CS${randSuffix.toString().slice(-3)}`;
      const fullName = `${firstName} ${lastName}`;

      const studentRecord = {
        id: `stu-${Date.now()}`,
        student_id: studentId,
        studentId: studentId,
        admission_no: admissionNo,
        admissionNo: admissionNo,
        enrollment_no: enrollmentNo,
        enrollmentNo: enrollmentNo,
        roll_no: rollNo,
        rollNo: rollNo,
        first_name: firstName,
        firstName: firstName,
        last_name: lastName,
        lastName: lastName,
        full_name: fullName,
        fullName: fullName,
        college_email: collegeEmail,
        collegeEmail: collegeEmail,
        personal_email: data.personalEmail || data.personal_email || `${firstName.toLowerCase()}@gmail.com`,
        personalEmail: data.personalEmail || data.personal_email || `${firstName.toLowerCase()}@gmail.com`,
        mobile: mobile,
        phone: mobile,
        department_id: data.departmentId || data.department_id || 'dept-cse',
        departmentId: data.departmentId || data.department_id || 'dept-cse',
        course_id: data.courseId || data.course_id || 'course-btech-cse',
        courseId: data.courseId || data.course_id || 'course-btech-cse',
        semester_number: Number(data.semesterNumber || data.semester_number || 1),
        semesterNumber: Number(data.semesterNumber || data.semester_number || 1),
        batch: data.batch || `${currentYear}-${currentYear + 4}`,
        status: data.status || 'Active',
        gender: data.gender || 'Male',
        blood_group: data.bloodGroup || data.blood_group || 'O+',
        bloodGroup: data.bloodGroup || data.blood_group || 'O+',
        photo: data.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200',
      };

      const credentials = {
        email: collegeEmail,
        username: collegeEmail,
        student_id: studentId,
        role: 'STUDENT',
        password: mobile,
        must_change_password: true,
      };

      return res.status(201).json({
        success: true,
        message: `Student ${fullName} registered successfully! Auto-generated Student ID: ${studentId}.`,
        student: studentRecord,
        credentials: credentials,
      });
    } catch (err: any) {
      return res.status(500).json({
        success: false,
        error: err.message || "Internal server error registering student.",
        message: err.message || "Internal server error registering student."
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Campus Connect ERP server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();

