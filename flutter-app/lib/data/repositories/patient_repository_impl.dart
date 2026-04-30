import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../core/config/api_config.dart';
import '../../domain/entities/patient.dart';
import '../../domain/entities/report.dart';
import '../../domain/repositories/patient_repository.dart';

class PatientRepositoryImpl implements PatientRepository {
  final http.Client _client;

  PatientRepositoryImpl(this._client);

  @override
  Future<bool> login({required String username, required String password}) async {
    if (username.isEmpty || password.isEmpty) return false;
    return true;
  }

  @override
  Future<List<Patient>> getPatients() async {
    // Placeholder for future backend endpoint integration.
    return const [
      Patient(id: 'P-1001', name: 'Asha Verma', age: 42, gender: 'Female'),
      Patient(id: 'P-1002', name: 'Rohan Mehta', age: 51, gender: 'Male'),
    ];
  }

  @override
  Future<void> uploadLabData({
    required String patientId,
    required Map<String, dynamic> labPayload,
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/analyze'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(labPayload),
    );
    if (response.statusCode >= 400) {
      throw Exception('Failed to upload lab data');
    }
  }

  @override
  Future<Report> getPatientReport(String patientId) async {
    // Placeholder until backend exposes patient report retrieval endpoint.
    return const Report(
      doctorSummary: 'No generated report available yet.',
      patientFriendlyExplanation: 'Your report will appear here after analysis is completed.',
    );
  }
}
