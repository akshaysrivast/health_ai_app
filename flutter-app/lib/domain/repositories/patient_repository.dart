import '../entities/patient.dart';
import '../entities/report.dart';

abstract class PatientRepository {
  Future<bool> login({required String username, required String password});

  Future<List<Patient>> getPatients();

  Future<void> uploadLabData({
    required String patientId,
    required Map<String, dynamic> labPayload,
  });

  Future<Report> getPatientReport(String patientId);
}
