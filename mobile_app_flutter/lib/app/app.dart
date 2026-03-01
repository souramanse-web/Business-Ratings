import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/api/api_client.dart';
import '../core/api/auth_api.dart';
import '../core/api/business_api.dart';
import '../features/auth/auth_provider.dart';
import 'router.dart';

class BusinessRatingMobileApp extends StatelessWidget {
  const BusinessRatingMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiClient = ApiClient();

    return MultiProvider(
      providers: [
        Provider<ApiClient>.value(value: apiClient),
        Provider<AuthApi>(create: (_) => AuthApi(apiClient.dio)),
        Provider<BusinessApi>(create: (_) => BusinessApi(apiClient.dio)),
        ChangeNotifierProvider<AuthProvider>(
          create: (context) => AuthProvider(context.read<AuthApi>()),
        ),
      ],
      child: Builder(
        builder: (context) {
          final authProvider = context.watch<AuthProvider>();
          final router = buildRouter(authProvider);

          return MaterialApp.router(
            title: 'Business Rating',
            debugShowCheckedModeBanner: false,
            routerConfig: router,
            theme: ThemeData(
              colorSchemeSeed: Colors.blue,
              useMaterial3: true,
            ),
          );
        },
      ),
    );
  }
}
