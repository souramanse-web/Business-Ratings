import 'package:dio/dio.dart';
import '../models/business.dart';
import '../models/rating.dart';

class BusinessApi {
  final Dio dio;
  BusinessApi(this.dio);

  Future<List<Business>> getBusinesses() async {
    final response = await dio.get('/api/businesses');
    final data = response.data as List<dynamic>;
    return data.map((json) => Business.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<List<Rating>> getRatingsForBusiness(int businessId) async {
    final response = await dio.get('/api/ratings/business/$businessId');
    final data = response.data as List<dynamic>;
    return data.map((json) => Rating.fromJson(json as Map<String, dynamic>)).toList();
  }

  Future<void> submitRating({required int businessId, required int score, required String comment}) async {
    await dio.post('/api/rate', data: {
      'business_id': businessId,
      'score': score,
      'comment': comment,
    });
  }
}
