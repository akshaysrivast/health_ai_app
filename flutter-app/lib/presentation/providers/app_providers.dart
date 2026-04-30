import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

import '../../data/repositories/patient_repository_impl.dart';
import '../../domain/entities/patient.dart';
import '../../domain/entities/report.dart';
import '../../domain/repositories/patient_repository.dart';

final httpClientProvider = Provider<http.Client>((ref) => http.Client());

final patientRepositoryProvider = Provider<PatientRepository>((ref) {
  return PatientRepositoryImpl(ref.read(httpClientProvider));
});

class AuthNotifier extends StateNotifier<bool> {
  AuthNotifier(this._repo) : super(false);
  final PatientRepository _repo;

  Future<bool> login(String username, String password) async {
    final ok = await _repo.login(username: username, password: password);
    state = ok;
    return ok;
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, bool>((ref) {
  return AuthNotifier(ref.read(patientRepositoryProvider));
});

final patientsProvider = FutureProvider<List<Patient>>((ref) {
  return ref.read(patientRepositoryProvider).getPatients();
});

final selectedPatientProvider = StateProvider<Patient?>((ref) => null);

final reportProvider = FutureProvider.family<Report, String>((ref, patientId) {
  return ref.read(patientRepositoryProvider).getPatientReport(patientId);
});
