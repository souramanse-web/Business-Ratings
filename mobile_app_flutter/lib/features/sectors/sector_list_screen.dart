import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../core/api/business_api.dart';
import '../../core/models/business.dart';

class SectorListScreen extends StatefulWidget {
  const SectorListScreen({super.key});

  @override
  State<SectorListScreen> createState() => _SectorListScreenState();
}

class _SectorListScreenState extends State<SectorListScreen> {
  late Future<List<String>> _sectorsFuture;

  @override
  void initState() {
    super.initState();
    _sectorsFuture = _loadSectors();
  }

  Future<List<String>> _loadSectors() async {
    final api = context.read<BusinessApi>();
    final businesses = await api.getBusinesses();
    final sectorNames = businesses
        .map((b) => b.sector ?? 'Other')
        .toSet()
        .toList()
      ..sort();
    return ['All', ...sectorNames];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sectors'),
        actions: [
          IconButton(
            onPressed: () => context.go('/profile'),
            icon: const Icon(Icons.person),
          )
        ],
      ),
      body: FutureBuilder<List<String>>(
        future: _sectorsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return const Center(child: Text('Failed to load sectors'));
          }

          final sectors = snapshot.data ?? <String>[];
          if (sectors.isEmpty) {
            return const Center(child: Text('No sectors found'));
          }

          return ListView.builder(
            itemCount: sectors.length,
            itemBuilder: (context, index) {
              final sector = sectors[index];
              return ListTile(
                leading: const Icon(Icons.apartment),
                title: Text(sector),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go('/businesses?sector=$sector'),
              );
            },
          );
        },
      ),
    );
  }
}
