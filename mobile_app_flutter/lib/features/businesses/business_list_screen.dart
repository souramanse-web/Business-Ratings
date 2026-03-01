import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../core/api/business_api.dart';
import '../../core/models/business.dart';

class BusinessListScreen extends StatefulWidget {
  final String sectorName;
  const BusinessListScreen({super.key, required this.sectorName});

  @override
  State<BusinessListScreen> createState() => _BusinessListScreenState();
}

class _BusinessListScreenState extends State<BusinessListScreen> {
  late Future<List<Business>> _businessesFuture;

  @override
  void initState() {
    super.initState();
    _businessesFuture = _loadBusinesses();
  }

  Future<List<Business>> _loadBusinesses() async {
    final api = context.read<BusinessApi>();
    final all = await api.getBusinesses();
    if (widget.sectorName == 'All') {
      return all;
    }
    return all.where((b) => (b.sector ?? 'Other') == widget.sectorName).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Businesses • ${widget.sectorName}')),
      body: FutureBuilder<List<Business>>(
        future: _businessesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return const Center(child: Text('Failed to load businesses'));
          }

          final businesses = snapshot.data ?? <Business>[];
          if (businesses.isEmpty) {
            return const Center(child: Text('No businesses found'));
          }

          return ListView.separated(
            itemCount: businesses.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final business = businesses[index];
              return ListTile(
                title: Text(business.name),
                subtitle: Text('⭐ ${business.averageRating.toStringAsFixed(1)} (${business.ratingCount})'),
                onTap: () => context.push('/business/${business.id}', extra: business),
              );
            },
          );
        },
      ),
    );
  }
}
