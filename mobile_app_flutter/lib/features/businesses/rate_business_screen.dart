import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/api/business_api.dart';
import '../../core/models/business.dart';

class RateBusinessScreen extends StatefulWidget {
  final Business business;
  const RateBusinessScreen({super.key, required this.business});

  @override
  State<RateBusinessScreen> createState() => _RateBusinessScreenState();
}

class _RateBusinessScreenState extends State<RateBusinessScreen> {
  int _score = 5;
  final _commentController = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _loading = true);
    try {
      await context.read<BusinessApi>().submitRating(
            businessId: widget.business.id,
            score: _score,
            comment: _commentController.text.trim(),
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Rating submitted')));
      Navigator.of(context).pop();
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to submit rating')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Rate ${widget.business.name}')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButtonFormField<int>(
              value: _score,
              items: List.generate(
                5,
                (i) => DropdownMenuItem(value: i + 1, child: Text('${i + 1} Star${i == 0 ? '' : 's'}')),
              ),
              onChanged: (v) => setState(() => _score = v ?? 5),
              decoration: const InputDecoration(labelText: 'Score'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _commentController,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'Comment',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _loading ? null : _submit,
                child: Text(_loading ? 'Submitting...' : 'Submit Rating'),
              ),
            )
          ],
        ),
      ),
    );
  }
}
