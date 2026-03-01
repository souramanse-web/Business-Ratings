class Business {
  final int id;
  final String name;
  final String description;
  final String? sector;
  final String? website;
  final String? location;
  final double averageRating;
  final int ratingCount;

  const Business({
    required this.id,
    required this.name,
    required this.description,
    required this.sector,
    required this.website,
    required this.location,
    required this.averageRating,
    required this.ratingCount,
  });

  factory Business.fromJson(Map<String, dynamic> json) {
    return Business(
      id: (json['id'] as num?)?.toInt() ?? 0,
      name: json['name']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      sector: json['sector']?.toString(),
      website: json['website']?.toString(),
      location: json['location']?.toString(),
      averageRating: (json['average_rating'] as num?)?.toDouble() ?? 0,
      ratingCount: (json['rating_count'] as num?)?.toInt() ?? 0,
    );
  }
}
