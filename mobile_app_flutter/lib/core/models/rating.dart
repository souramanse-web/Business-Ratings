class Rating {
  final int id;
  final int score;
  final String? comment;
  final String username;
  final String createdAt;

  const Rating({
    required this.id,
    required this.score,
    required this.comment,
    required this.username,
    required this.createdAt,
  });

  factory Rating.fromJson(Map<String, dynamic> json) {
    return Rating(
      id: (json['id'] as num?)?.toInt() ?? 0,
      score: (json['score'] as num?)?.toInt() ?? 0,
      comment: json['comment']?.toString(),
      username: json['username']?.toString() ?? 'Unknown',
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}
