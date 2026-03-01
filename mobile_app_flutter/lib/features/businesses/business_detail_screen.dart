import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../core/api/business_api.dart';
import '../../core/models/business.dart';
import '../../core/models/rating.dart';

class BusinessDetailScreen extends StatefulWidget {
  final Business business;
  const BusinessDetailScreen({super.key, required this.business});

  @override
  State<BusinessDetailScreen> createState() => _BusinessDetailScreenState();
}

class _BusinessDetailScreenState extends State<BusinessDetailScreen> {
  late Future<List<Rating>> _ratingsFuture;

  @override
  void initState() {
    super.initState();
    _ratingsFuture = context.read<BusinessApi>().getRatingsForBusiness(widget.business.id);
  }

  @override
  Widget build(BuildContext context) {
    final business = widget.business;

    return Scaffold(
      appBar: AppBar(title: Text(business.name)),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          await context.push('/rate/${business.id}', extra: business);
          if (!mounted) return;
          setState(() {
            _ratingsFuture = context.read<BusinessApi>().getRatingsForBusiness(business.id);
          });
        },
        icon: const Icon(Icons.star),
        label: const Text('Rate'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(business.description),
            const SizedBox(height: 8),
            if ((business.location ?? '').isNotEmpty) Text('Location: ${business.location}'),
            if ((business.website ?? '').isNotEmpty) Text('Website: ${business.website}'),
            const SizedBox(height: 12),
            Text('Ratings', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Expanded(
              child: FutureBuilder<List<Rating>>(
                future: _ratingsFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  if (snapshot.hasError) {
                    return const Center(child: Text('Failed to load ratings'));
                  }

                  final ratings = snapshot.data ?? <Rating>[];
                  if (ratings.isEmpty) {
                    return const Center(child: Text('No ratings yet'));
                  }

                  return ListView.separated(
                    itemCount: ratings.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, index) {
                      final r = ratings[index];
                      return ListTile(
                        title: Text('${r.username} • ${'★' * r.score}'),
                        subtitle: Text((r.comment ?? '').isEmpty ? 'No comment' : r.comment!),
                      );
                    },
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }
}
