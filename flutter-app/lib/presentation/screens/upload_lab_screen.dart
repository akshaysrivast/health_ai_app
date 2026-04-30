import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/app_providers.dart';

class UploadLabScreen extends ConsumerStatefulWidget {
  const UploadLabScreen({super.key});

  @override
  ConsumerState<UploadLabScreen> createState() => _UploadLabScreenState();
}

class _UploadLabScreenState extends ConsumerState<UploadLabScreen> {
  final _hba1cController = TextEditingController();
  final _glucoseController = TextEditingController();
  String _status = '';

  @override
  Widget build(BuildContext context) {
    final patient = ref.watch(selectedPatientProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Lab Data')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text('Patient: ${patient?.name ?? 'Unknown'}'),
            TextField(
              controller: _hba1cController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'HbA1c'),
            ),
            TextField(
              controller: _glucoseController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Fasting Glucose'),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: patient == null
                  ? null
                  : () async {
                      final payload = {
                        "demographics": {"patient_id": patient.id, "name": patient.name},
                        "labs": [
                          {"name": "hba1c", "value": double.tryParse(_hba1cController.text) ?? 0},
                          {"name": "fasting_glucose", "value": double.tryParse(_glucoseController.text) ?? 0}
                        ],
                        "anthropometry": {},
                        "lifestyle": {},
                        "history": {},
                        "features": {},
                        "risks": {},
                        "diagnosis": {},
                        "plan": {}
                      };

                      try {
                        await ref.read(patientRepositoryProvider).uploadLabData(
                              patientId: patient.id,
                              labPayload: payload,
                            );
                        if (!mounted) return;
                        setState(() => _status = 'Lab data uploaded successfully');
                      } catch (_) {
                        if (!mounted) return;
                        setState(() => _status = 'Upload failed');
                      }
                    },
              child: const Text('Submit'),
            ),
            const SizedBox(height: 8),
            Text(_status),
          ],
        ),
      ),
    );
  }
}
