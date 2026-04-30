import 'package:go_router/go_router.dart';

import '../screens/login_screen.dart';
import '../screens/patient_detail_screen.dart';
import '../screens/patient_list_screen.dart';
import '../screens/report_screen.dart';
import '../screens/upload_lab_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/patients', builder: (_, __) => const PatientListScreen()),
    GoRoute(path: '/patient-detail', builder: (_, __) => const PatientDetailScreen()),
    GoRoute(path: '/upload-lab', builder: (_, __) => const UploadLabScreen()),
    GoRoute(path: '/report', builder: (_, __) => const ReportScreen()),
  ],
);
