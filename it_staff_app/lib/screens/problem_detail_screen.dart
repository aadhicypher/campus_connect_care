import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProblemDetailScreen extends StatefulWidget {
  final Map<String, dynamic> problem;
  const ProblemDetailScreen({super.key, required this.problem});

  @override
  State<ProblemDetailScreen> createState() => _ProblemDetailScreenState();
}

class _ProblemDetailScreenState extends State<ProblemDetailScreen> {
  late String _currentStatus;
  bool _isUpdating = false;

  @override
  void initState() {
    super.initState();
    _currentStatus = widget.problem['status'];
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'Open':
        return const Color(0xFFE53935);
      case 'In Progress':
        return const Color(0xFFFFB300);
      case 'Resolved':
        return const Color(0xFF00C853);
      default:
        return Colors.grey;
    }
  }

  Color _severityColor(String severity) {
    switch (severity) {
      case 'critical':
        return const Color(0xFFE53935);
      case 'warning':
        return const Color(0xFFFFB300);
      default:
        return const Color(0xFF00C853);
    }
  }

  Future<void> _updateStatus(String newStatus) async {
    setState(() => _isUpdating = true);
    final success = await ApiService.updateProblemStatus(
        widget.problem['id'], newStatus);
    setState(() {
      _isUpdating = false;
      if (success) _currentStatus = newStatus;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success
            ? 'Status updated to $newStatus'
            : 'Failed to update status'),
        backgroundColor:
            success ? _statusColor(newStatus) : Colors.red,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final problem = widget.problem;
    final steps = problem['steps'] as List;
    final severityColor = _severityColor(problem['severity']);
    final statusColor = _statusColor(_currentStatus);

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Problem Details',
          style: TextStyle(
            color: Color(0xFF262626),
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        iconTheme: const IconThemeData(color: Color(0xFF262626)),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Divider(color: Colors.grey.shade200, height: 1),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            // Problem header card
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 12,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Severity color bar
                  Container(
                    height: 5,
                    decoration: BoxDecoration(
                      color: severityColor,
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: severityColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Icon(Icons.warning_amber_rounded,
                                  color: severityColor, size: 22),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                problem['type'],
                                style: const TextStyle(
                                  color: Color(0xFF262626),
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          problem['description'],
                          style: const TextStyle(
                            color: Color(0xFF8E8E8E),
                            fontSize: 14,
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Divider(color: Colors.grey.shade100),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Icon(Icons.router_outlined,
                                size: 15,
                                color: Colors.grey.shade400),
                            const SizedBox(width: 6),
                            Text(
                              problem['deviceName'],
                              style: const TextStyle(
                                color: Color(0xFF8E8E8E),
                                fontSize: 13,
                              ),
                            ),
                            const Spacer(),
                            Icon(Icons.access_time,
                                size: 15,
                                color: Colors.grey.shade400),
                            const SizedBox(width: 6),
                            Text(
                              problem['time'],
                              style: const TextStyle(
                                color: Color(0xFF8E8E8E),
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Assigned to + status card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 12,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 24,
                    backgroundColor:
                        const Color(0xFF833AB4).withOpacity(0.1),
                    child: Text(
                      problem['assignedTo'][0].toUpperCase(),
                      style: const TextStyle(
                        color: Color(0xFF833AB4),
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Assigned To',
                        style: TextStyle(
                          color: Color(0xFF8E8E8E),
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        problem['assignedTo'],
                        style: const TextStyle(
                          color: Color(0xFF262626),
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      _currentStatus,
                      style: TextStyle(
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Steps header
            const Padding(
              padding: EdgeInsets.only(left: 4, bottom: 12),
              child: Text(
                'Steps to Resolve',
                style: TextStyle(
                  color: Color(0xFF262626),
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            // Steps list
            ...steps.asMap().entries.map((entry) {
              final index = entry.key;
              final step = entry.value;
              return Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 28,
                      height: 28,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            Color(0xFF833AB4),
                            Color(0xFFE1306C),
                          ],
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Center(
                        child: Text(
                          '${index + 1}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        step.toString(),
                        style: const TextStyle(
                          color: Color(0xFF262626),
                          fontSize: 14,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 20),

            // Action buttons
            if (_isUpdating)
              const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Color(0xFFE1306C),
                  ),
                ),
              )
            else if (_currentStatus == 'Open')
              _actionButton(
                label: 'Mark as In Progress',
                icon: Icons.play_arrow_rounded,
                colors: [
                  const Color(0xFFFFB300),
                  const Color(0xFFFF8F00),
                ],
                onTap: () => _updateStatus('In Progress'),
              )
            else if (_currentStatus == 'In Progress')
              _actionButton(
                label: 'Mark as Resolved',
                icon: Icons.check_circle_rounded,
                colors: [
                  const Color(0xFF00C853),
                  const Color(0xFF00897B),
                ],
                onTap: () => _updateStatus('Resolved'),
              )
            else if (_currentStatus == 'Resolved')
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF00C853).withOpacity(0.08),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: const Color(0xFF00C853).withOpacity(0.3),
                  ),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.check_circle_rounded,
                        color: Color(0xFF00C853), size: 22),
                    SizedBox(width: 10),
                    Text(
                      'Problem Resolved ✓',
                      style: TextStyle(
                        color: Color(0xFF00C853),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _actionButton({
    required String label,
    required IconData icon,
    required List<Color> colors,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        height: 52,
        decoration: BoxDecoration(
          gradient: LinearGradient(colors: colors),
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
              color: colors[0].withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 8),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}