import 'package:flutter/material.dart';
import 'problem_detail_screen.dart';
import '../services/api_service.dart';

class ProblemsScreen extends StatefulWidget {
  final String? deviceId;
  const ProblemsScreen({super.key, this.deviceId});

  @override
  State<ProblemsScreen> createState() => _ProblemsScreenState();
}

class _ProblemsScreenState extends State<ProblemsScreen> {
  String _selectedStatus = 'All';
  final List<String> _statusFilters = [
    'All',
    'Open',
    'In Progress',
    'Resolved'
  ];
  List<Map<String, dynamic>> problems = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProblems();
  }

  Future<void> _loadProblems() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getProblems();
    setState(() {
      problems = data;
      _isLoading = false;
    });
  }

  List<Map<String, dynamic>> get _filteredProblems {
    var list = problems;
    if (widget.deviceId != null) {
      list =
          list.where((p) => p['deviceId'] == widget.deviceId).toList();
    }
    if (_selectedStatus != 'All') {
      list =
          list.where((p) => p['status'] == _selectedStatus).toList();
    }
    return list;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: Text(
          widget.deviceId != null ? 'Device Problems' : 'All Problems',
          style: const TextStyle(
            color: Color(0xFF262626),
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        iconTheme: const IconThemeData(color: Color(0xFF262626)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF262626)),
            onPressed: _loadProblems,
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Divider(color: Colors.grey.shade200, height: 1),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(
                  Color(0xFFE1306C),
                ),
              ),
            )
          : Column(
              children: [
                // Filter chips
                Container(
                  color: Colors.white,
                  padding: const EdgeInsets.symmetric(
                      vertical: 12, horizontal: 16),
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _statusFilters.map((status) {
                        final isSelected = _selectedStatus == status;
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: GestureDetector(
                            onTap: () => setState(
                                () => _selectedStatus = status),
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 8),
                              decoration: BoxDecoration(
                                gradient: isSelected
                                    ? const LinearGradient(
                                        colors: [
                                          Color(0xFF833AB4),
                                          Color(0xFFE1306C),
                                        ],
                                      )
                                    : null,
                                color: isSelected
                                    ? null
                                    : const Color(0xFFF5F5F5),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                status,
                                style: TextStyle(
                                  color: isSelected
                                      ? Colors.white
                                      : const Color(0xFF262626),
                                  fontWeight: FontWeight.w600,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),
                Divider(color: Colors.grey.shade200, height: 1),

                // Problems list
                Expanded(
                  child: _filteredProblems.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.check_circle_outline,
                                  size: 60,
                                  color: Colors.grey.shade300),
                              const SizedBox(height: 12),
                              const Text(
                                'No problems found',
                                style: TextStyle(
                                  color: Color(0xFF8E8E8E),
                                  fontSize: 16,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _filteredProblems.length,
                          itemBuilder: (context, index) {
                            return _problemCard(
                                _filteredProblems[index]);
                          },
                        ),
                ),
              ],
            ),
    );
  }

  Widget _problemCard(Map<String, dynamic> problem) {
    final severityColor = _severityColor(problem['severity']);
    final statusColor = _statusColor(problem['status']);

    return GestureDetector(
      onTap: () async {
        await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ProblemDetailScreen(problem: problem),
          ),
        );
        _loadProblems();
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
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
            // Severity bar at top
            Container(
              height: 4,
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
                      Expanded(
                        child: Text(
                          problem['type'],
                          style: const TextStyle(
                            color: Color(0xFF262626),
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          problem['status'],
                          style: TextStyle(
                            color: statusColor,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Icon(Icons.router_outlined,
                          size: 14, color: Colors.grey.shade400),
                      const SizedBox(width: 4),
                      Text(
                        problem['deviceName'],
                        style: const TextStyle(
                          color: Color(0xFF8E8E8E),
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    problem['description'],
                    style: const TextStyle(
                      color: Color(0xFFB0B0B0),
                      fontSize: 12,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 12),
                  Divider(color: Colors.grey.shade100, height: 1),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 12,
                        backgroundColor:
                            const Color(0xFF833AB4).withOpacity(0.1),
                        child: Text(
                          problem['assignedTo'][0].toUpperCase(),
                          style: const TextStyle(
                            color: Color(0xFF833AB4),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        problem['assignedTo'],
                        style: const TextStyle(
                          color: Color(0xFF8E8E8E),
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const Spacer(),
                      Icon(Icons.access_time,
                          size: 13, color: Colors.grey.shade400),
                      const SizedBox(width: 4),
                      Text(
                        problem['time'],
                        style: const TextStyle(
                          color: Color(0xFFB0B0B0),
                          fontSize: 12,
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
    );
  }
}