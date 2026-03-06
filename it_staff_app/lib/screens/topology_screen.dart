import 'package:flutter/material.dart';
import 'problems_screen.dart';
import '../services/api_service.dart';

class TopologyScreen extends StatefulWidget {
  const TopologyScreen({super.key});

  @override
  State<TopologyScreen> createState() => _TopologyScreenState();
}

class _TopologyScreenState extends State<TopologyScreen> {
  List<Map<String, dynamic>> devices = [];
  bool _isLoading = true;
  String _selectedFilter = 'All';
  final List<String> _filters = ['All', 'Critical', 'Warning', 'OK'];

  @override
  void initState() {
    super.initState();
    _loadDevices();
  }

  Future<void> _loadDevices() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getDevices();
    setState(() {
      devices = data;
      _isLoading = false;
    });
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'ok':
        return const Color(0xFF00C853);
      case 'warning':
        return const Color(0xFFFFB300);
      case 'critical':
        return const Color(0xFFE53935);
      default:
        return Colors.grey;
    }
  }

  IconData _deviceIcon(String type) {
    switch (type) {
      case 'switch':
        return Icons.device_hub;
      case 'camera':
        return Icons.videocam_outlined;
      case 'dvr':
        return Icons.video_settings_outlined;
      default:
        return Icons.devices_outlined;
    }
  }

  List<Map<String, dynamic>> get _filteredDevices {
    if (_selectedFilter == 'All') return devices;
    return devices
        .where((d) => d['status'] == _selectedFilter.toLowerCase())
        .toList();
  }

  int get _criticalCount =>
      devices.where((d) => d['status'] == 'critical').length;
  int get _warningCount =>
      devices.where((d) => d['status'] == 'warning').length;
  int get _okCount => devices.where((d) => d['status'] == 'ok').length;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Network Topology',
          style: TextStyle(
            color: Color(0xFF262626),
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.warning_amber_outlined,
                color: Color(0xFF262626)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (_) => const ProblemsScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF262626)),
            onPressed: _loadDevices,
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
                // Status summary
                Container(
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.06),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      _statusTile('Critical', _criticalCount,
                          const Color(0xFFE53935)),
                      _divider(),
                      _statusTile('Warning', _warningCount,
                          const Color(0xFFFFB300)),
                      _divider(),
                      _statusTile('OK', _okCount,
                          const Color(0xFF00C853)),
                    ],
                  ),
                ),

                // Filter chips
                SizedBox(
                  height: 44,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    children: _filters.map((filter) {
                      final isSelected = _selectedFilter == filter;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: GestureDetector(
                          onTap: () =>
                              setState(() => _selectedFilter = filter),
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
                              filter,
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
                const SizedBox(height: 12),

                // Device list
                Expanded(
                  child: devices.isEmpty
                      ? const Center(
                          child: Text(
                            'No devices found',
                            style: TextStyle(
                                color: Color(0xFF8E8E8E), fontSize: 16),
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 4),
                          itemCount: _filteredDevices.length,
                          itemBuilder: (context, index) {
                            return _deviceCard(_filteredDevices[index]);
                          },
                        ),
                ),
              ],
            ),
    );
  }

  Widget _statusTile(String label, int count, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(
            count.toString(),
            style: TextStyle(
              color: color,
              fontSize: 26,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
                color: Color(0xFF8E8E8E),
                fontSize: 12,
                fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Widget _divider() {
    return Container(
      width: 1,
      height: 36,
      color: Colors.grey.shade200,
    );
  }

  Widget _deviceCard(Map<String, dynamic> device) {
    final color = _statusColor(device['status']);
    final connections = device['connectedTo'];
    int connectionCount = 0;
    if (connections is List) connectionCount = connections.length;

    return GestureDetector(
      onTap: () {
        if (device['status'] != 'ok') {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ProblemsScreen(deviceId: device['id']),
            ),
          );
        }
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
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
          border: Border.all(
            color: color.withOpacity(0.2),
            width: 1.5,
          ),
        ),
        child: Row(
          children: [
            // Device icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(_deviceIcon(device['type']),
                  color: color, size: 24),
            ),
            const SizedBox(width: 14),

            // Device info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    device['name'],
                    style: const TextStyle(
                      color: Color(0xFF262626),
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    device['ip'],
                    style: const TextStyle(
                        color: Color(0xFF8E8E8E), fontSize: 12),
                  ),
                  if (connectionCount > 0) ...[
                    const SizedBox(height: 2),
                    Text(
                      'Connected to $connectionCount device(s)',
                      style: const TextStyle(
                          color: Color(0xFFB0B0B0), fontSize: 11),
                    ),
                  ],
                ],
              ),
            ),

            // Status indicator
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 7,
                        height: 7,
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 5),
                      Text(
                        device['status'].toUpperCase(),
                        style: TextStyle(
                          color: color,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                if (device['status'] != 'ok') ...[
                  const SizedBox(height: 6),
                  const Text(
                    'Tap to view',
                    style: TextStyle(
                        color: Color(0xFF0095F6),
                        fontSize: 11,
                        fontWeight: FontWeight.w500),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}