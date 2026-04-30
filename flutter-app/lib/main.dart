import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'presentation/router/app_router.dart';

void main() {
  runApp(const ProviderScope(child: MetabolicAiApp()));
}

class MetabolicAiApp extends StatelessWidget {
  const MetabolicAiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Metabolic AI',
      theme: ThemeData(colorSchemeSeed: Colors.teal),
      routerConfig: appRouter,
    );
  }
}
