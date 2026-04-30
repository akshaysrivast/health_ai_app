import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/app_providers.dart';

class ReportScreen extends ConsumerWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final patient = ref.watch(selectedPatientProvider);
    if (patient == null) {
      return const Scaffold(body: Center(child: Text('No patient selected')));
    }

    final reportAsync = ref.watch(reportProvider(patient.id));

    return Scaffold(
      appBar: AppBar(title: const Text('Report')),
      body: reportAsync.when(
        data: (report) => Padding(
          padding: const EdgeInsets.all(16),
          child: ListView(
            children: [
              Text('Doctor Summary', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(report.doctorSummary),
              const SizedBox(height: 16),
              Text('Patient Explanation', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(report.patientFriendlyExplanation),
            ],
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Failed to load report: $e')),
      ),
    );
  }
}
