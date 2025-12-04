part of '../user.dart';

class UserService {
  static User? _currentUser;
  static User? get currentUser => _currentUser;

  static final SupabaseClient _client = Supabase.instance.client;
  static final ImagePicker _imagePicker = ImagePicker();

  static Future<Result<User, String>> login({
    required String email,
    required String password,
  }) async {
    try {
      final authResponse = await _client.auth.signInWithPassword(
        email: email,
        password: password,
      );

      if (authResponse.user == null) {
        return Failure('Erro ao fazer login: usuário não encontrado');
      }

      final userResponse = await _client
          .from('users')
          .select()
          .eq('uuid', authResponse.user!.id)
          .single();

      final user = User.fromMap(userResponse);
      _currentUser = user;

      return Success(user);
    } on AuthException catch (e) {
      switch (e.message) {
        case 'Invalid login credentials':
          return Failure('Email ou senha incorretos');
        case 'Email not confirmed':
          return Failure('Email não confirmado. Verifique sua caixa de entrada');
        case 'Too many requests':
          return Failure('Muitas tentativas. Tente novamente mais tarde');
        default:
          return Failure('Erro ao fazer login: ${e.message}');
      }
    } catch (e) {
      return Failure('Erro inesperado ao fazer entrar');
    }
  }

  // Registro do usuário
  static Future<Result<User, String>> register({
    required String name,
    required String email,
    required String password,
  }) async {
    try {
      // Validações básicas
      if (name.trim().isEmpty) {
        return Failure('Nome não pode estar vazio');
      }
      if (email.trim().isEmpty || !email.contains('@')) {
        return Failure('Email inválido');
      }
      if (password.length < 8) {
        return Failure('Senha deve ter pelo menos 8 caracteres');
      }

      // Criar conta no Supabase Auth
      final authResponse = await _client.auth.signUp(
        email: email,
        password: password,
      );

      if (authResponse.user == null) {
        return Failure('Erro ao criar conta');
      }

      final userData = {
        'uuid': authResponse.user!.id,
        'name': name.trim(),
        'email': email.trim().toLowerCase(),
        'photo': false,
      };

      await _client.from('users').insert(userData);

      final user = User.fromMap({
        ...userData,
        'created_at': DateTime.now().toIso8601String(),
      });

      _currentUser = user;
      return Success(user);
    } on AuthException catch (e) {
      switch (e.message) {
        case 'User already registered':
          return Failure('Email já está em uso');
        case 'Password should be at least 6 characters':
          return Failure('Senha deve ter pelo menos 6 caracteres');
        case 'Unable to validate email address: invalid format':
          return Failure('Formato de email inválido');
        default:
          return Failure('Erro ao criar conta: ${e.message}');
      }
    } catch (e) {
      return Failure('Erro inesperado ao criar conta');
    }
  }

  // Logout do usuário
  static Future<Result<bool, String>> logout() async {
    try {
      await _client.auth.signOut();
      _currentUser = null;
      return Success(true);
    } catch (e) {
      return Failure('Erro ao fazer logout');
    }
  }

  // Editar dados do usuário
  static Future<Result<User, String>> editUser({
    String? name,
    String? email,
  }) async {
    try {
      if (_currentUser == null) {
        return Failure('Usuário não está logado');
      }

      final updates = <String, dynamic>{};
      
      if (name != null && name.trim().isNotEmpty) {
        updates['name'] = name.trim();
      }
      
      if (email != null && email.trim().isNotEmpty) {
        if (!email.contains('@')) {
          return Failure('Email inválido');
        }
        updates['email'] = email.trim().toLowerCase();
        
        // Atualizar email no auth também
        await _client.auth.updateUser(UserAttributes(email: email.trim().toLowerCase()));
      }

      if (updates.isEmpty) {
        return Failure('Nenhuma alteração fornecida');
      }

      // Atualizar na tabela users
      final response = await _client
          .from('users')
          .update(updates)
          .eq('uuid', _currentUser!.uuid)
          .select()
          .single();

      final updatedUser = User.fromMap(response);
      _currentUser = updatedUser;

      return Success(updatedUser);
    } on AuthException catch (e) {
      return Failure('Erro ao atualizar email: ${e.message}');
    } catch (e) {
      return Failure('Erro ao atualizar dados do usuário');
    }
  }

  // Editar foto do usuário
  static Future<Result<User, String>> editUserPhoto({
    ImageSource source = ImageSource.gallery,
  }) async {
    try {
      if (_currentUser == null) {
        return Failure('Usuário não está logado');
      }

      // Selecionar imagem
      final pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 500,
        maxHeight: 500,
        imageQuality: 80,
      );

      if (pickedFile == null) {
        return Failure('Nenhuma imagem selecionada');
      }

      final file = File(pickedFile.path);
      final fileName = '${_currentUser!.uuid}.jpg';

      // Upload para Supabase Storage
      await _client.storage
          .from('user-pictures')
          .upload(fileName, file, fileOptions: const FileOptions(upsert: true));

      // Atualizar flag de foto na tabela users
      final response = await _client
          .from('users')
          .update({'photo': true})
          .eq('uuid', _currentUser!.uuid)
          .select()
          .single();

      final updatedUser = User.fromMap(response);
      _currentUser = updatedUser;

      return Success(updatedUser);
    } catch (e) {
      return Failure('Erro ao atualizar foto do usuário');
    }
  }

  // Remover foto do usuário
  static Future<Result<User, String>> removeUserPhoto() async {
    try {
      if (_currentUser == null) {
        return Failure('Usuário não está logado');
      }

      final fileName = '${_currentUser!.uuid}.jpg';

      // Remover do storage
      await _client.storage
          .from('user-pictures')
          .remove([fileName]);

      // Atualizar flag de foto na tabela users
      final response = await _client
          .from('users')
          .update({'photo': false})
          .eq('uuid', _currentUser!.uuid)
          .select()
          .single();

      final updatedUser = User.fromMap(response);
      _currentUser = updatedUser;

      return Success(updatedUser);
    } catch (e) {
      return Failure('Erro ao remover foto do usuário');
    }
  }

  // Editar senha do usuário
  static Future<Result<User, String>> editPassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      if (_currentUser == null) {
        return Failure('Usuário não está logado');
      }

      if (newPassword.length < 6) {
        return Failure('Nova senha deve ter pelo menos 6 caracteres');
      }

      // Verificar senha atual fazendo login temporário
      final signInResult = await _client.auth.signInWithPassword(
        email: _currentUser!.email,
        password: currentPassword,
      );

      if (signInResult.user == null) {
        return Failure('Senha atual incorreta');
      }

      // Atualizar senha
      await _client.auth.updateUser(
        UserAttributes(password: newPassword),
      );

      return Success(_currentUser!);
    } on AuthException catch (e) {
      switch (e.message) {
        case 'Invalid login credentials':
          return Failure('Senha atual incorreta');
        case 'Password should be at least 6 characters':
          return Failure('Nova senha deve ter pelo menos 6 caracteres');
        default:
          return Failure('Erro ao atualizar senha: ${e.message}');
      }
    } catch (e) {
      return Failure('Erro ao atualizar senha');
    }
  }

  // Verificar se usuário já está logado
  static Future<Result<User?, String>> checkCurrentUser() async {
    try {
      final session = _client.auth.currentSession;
      if (session == null) {
        _currentUser = null;
        return Success(null);
      }

      // Buscar dados do usuário
      final userResponse = await _client
          .from('users')
          .select()
          .eq('uuid', session.user.id)
          .single();

      final user = User.fromMap(userResponse);
      _currentUser = user;

      return Success(user);
    } catch (e) {
      _currentUser = null;
      return Failure('Erro ao verificar usuário atual');
    }
  }
}
