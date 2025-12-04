part of '../user.dart';

class User {
  final String uuid;
  final DateTime createdAt;
  final String name;
  final String email;
  final bool photo;

  const User({
    required this.uuid,
    required this.createdAt,
    required this.name,
    required this.email,
    required this.photo,
  });

  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      uuid: map['uuid'] as String,
      createdAt: DateTime.parse(map['created_at'] as String),
      name: map['name'] as String,
      email: map['email'] as String,
      photo: map['photo'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'uuid': uuid,
      'created_at': createdAt.toIso8601String(),
      'name': name,
      'email': email,
      'photo': photo,
    };
  }

  User copyWith({
    String? uuid,
    DateTime? createdAt,
    String? name,
    String? email,
    bool? photo,
  }) {
    return User(
      uuid: uuid ?? this.uuid,
      createdAt: createdAt ?? this.createdAt,
      name: name ?? this.name,
      email: email ?? this.email,
      photo: photo ?? this.photo,
    );
  }

  String get photoUrl => photo 
    ? Supabase.instance.client.storage
        .from('user-pictures')
        .getPublicUrl('$uuid.jpg')
    : '';

  @override
  String toString() {
    return 'User(uuid: $uuid, name: $name, email: $email, photo: $photo)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.uuid == uuid;
  }

  @override
  int get hashCode {
    return uuid.hashCode;
  }
}
