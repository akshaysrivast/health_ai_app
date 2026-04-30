import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/app_providers.dart';

class PatientDetailScreen extends ConsumerWidget {
  const PatientDetailScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final patient = ref.watch(selectedPatientProvider);
    if (patient == null) {
      return const Scaffold(body: Center(child: Text('No patient selected')));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Patient Detail')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(patient.name, style: Theme.of(context).textTheme.headlineSmall),
            Text('Patient ID: ${patient.id}'),
            Text('Age: ${patient.age}'),
            Text('Gender: ${patient.gender}'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => context.go('/upload-lab'),
              child: const Text('Upload Lab Data'),
            ),
            ElevatedButton(
              onPressed: () => context.go('/report'),
              child: const Text('View Report'),
            ),
          ],
        ),
      ),
    );
  }
}
