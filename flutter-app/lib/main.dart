import 'package:flutter/material.dart';

void main() {
  runApp(const MetabolicAiApp());
}

class MetabolicAiApp extends StatelessWidget {
  const MetabolicAiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Metabolic AI',
      theme: ThemeData(colorSchemeSeed: Colors.teal),
      home: const Scaffold(
        body: Center(
          child: Text('Metabolic AI Platform'),
        ),
      ),
    );
  }
}
