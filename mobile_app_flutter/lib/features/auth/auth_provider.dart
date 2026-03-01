import 'package:flutter/foundation.dart';
import '../../core/api/auth_api.dart';

class AuthProvider extends ChangeNotifier {
  final AuthApi _authApi;
  bool _isAuthenticated = false;
  String? _error;

  AuthProvider(this._authApi);

  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;

  Future<bool> login(String username, String password) async {
    try {
      _error = null;
      await _authApi.login(username: username, password: password);
      _isAuthenticated = true;
      notifyListeners();
      return true;
    } catch (_) {
      _error = 'Invalid credentials or server error.';
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(String username, String email, String password) async {
    try {
      _error = null;
      await _authApi.register(username: username, email: email, password: password);
      return await login(username, password);
    } catch (_) {
      _error = 'Registration failed.';
      notifyListeners();
      return false;
    }
  }

  void logout() {
    _isAuthenticated = false;
    notifyListeners();
  }
}
