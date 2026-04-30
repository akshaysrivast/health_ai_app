import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/app_providers.dart';

class PatientListScreen extends ConsumerWidget {
  const PatientListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final patientsAsync = ref.watch(patientsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Patients')),
      body: patientsAsync.when(
        data: (patients) => ListView.builder(
          itemCount: patients.length,
          itemBuilder: (context, index) {
            final patient = patients[index];
            return ListTile(
              title: Text(patient.name),
              subtitle: Text('${patient.gender}, ${patient.age} years'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                ref.read(selectedPatientProvider.notifier).state = patient;
                context.go('/patient-detail');
              },
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Failed to load patients: $e')),
      ),
    );
  }
}
