import 'package:dio/dio.dart';

class AuthApi {
  final Dio dio;
  AuthApi(this.dio);

  Future<void> login({required String username, required String password}) async {
    await dio.post('/login', data: {'username': username, 'password': password});
  }

  Future<void> register({required String username, required String email, required String password}) async {
    await dio.post('/register', data: {
      'username': username,
      'email': email,
      'password': password,
    });
  }
}
