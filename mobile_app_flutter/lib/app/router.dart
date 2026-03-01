import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../core/models/business.dart';
import '../features/auth/auth_provider.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/businesses/business_detail_screen.dart';
import '../features/businesses/business_list_screen.dart';
import '../features/businesses/rate_business_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/sectors/sector_list_screen.dart';

GoRouter buildRouter(AuthProvider authProvider) {
  return GoRouter(
    initialLocation: '/login',
    refreshListenable: authProvider,
    redirect: (context, state) {
      final isAuth = authProvider.isAuthenticated;
      final isAuthRoute = state.matchedLocation == '/login' || state.matchedLocation == '/register';

      if (!isAuth && !isAuthRoute) {
        return '/login';
      }

      if (isAuth && isAuthRoute) {
        return '/sectors';
      }

      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
      GoRoute(path: '/sectors', builder: (context, state) => const SectorListScreen()),
      GoRoute(
        path: '/businesses',
        builder: (context, state) {
          final sectorName = state.uri.queryParameters['sector'] ?? 'All';
          return BusinessListScreen(sectorName: sectorName);
        },
      ),
      GoRoute(
        path: '/business/:id',
        builder: (context, state) {
          final business = state.extra as Business;
          return BusinessDetailScreen(business: business);
        },
      ),
      GoRoute(
        path: '/rate/:id',
        builder: (context, state) {
          final business = state.extra as Business;
          return RateBusinessScreen(business: business);
        },
      ),
      GoRoute(path: '/profile', builder: (context, state) => const ProfileScreen()),
    ],
  );
}
