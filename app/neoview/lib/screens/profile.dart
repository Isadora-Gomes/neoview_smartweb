import 'package:flutter/material.dart';
import 'package:flutter_tools/form_validator.dart';
import 'package:flutter_tools/screen_observer.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/rules.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/navigation.dart';
import 'package:neoview/features/user.dart';
import 'package:dart_tools/result.dart';
import 'package:neoview/widgets/app_button.dart';
import 'package:neoview/widgets/app_inut.dart';

class Profile extends StatefulWidget {
  const Profile({super.key});

  @override
  State<Profile> createState() => _ProfileState();
}

class _ProfileState extends State<Profile> with WidgetsBindingObserver, ScreenObserver {
  final InputEdittingController<String> nameController = InputEdittingController("", AppRules.name);
  final InputEdittingController<String> emailController = InputEdittingController("", AppRules.email);
  final InputEdittingController<String> currentPasswordController = InputEdittingController("", AppRules.password);
  final InputEdittingController<String> newPasswordController = InputEdittingController("", AppRules.password);
  final InputEdittingController<String> confirmPasswordController = InputEdittingController("", AppRules.password);

  final InputSecretController currentPasswordSecret = InputSecretController();
  final InputSecretController newPasswordSecret = InputSecretController();
  final InputSecretController confirmPasswordSecret = InputSecretController();

  bool _isLoading = false;
  User? _currentUser;

  @override
  void initState() {
    WidgetsBinding.instance.addObserver(this);
    _loadUserData();
    super.initState();
  }

  void _loadUserData() {
    setState(() {
      _currentUser = UserService.currentUser;
    });
    if (_currentUser != null) {
      nameController.value = _currentUser!.name;
      emailController.value = _currentUser!.email;
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _loadUserData();
    }
  }

  @override
  void onKeyboardOpen() => setState(() {});
  @override
  void onKeyboardClose() => setState(() {});

  Future<void> _handleSaveChanges() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final needsUserUpdate = 
        nameController.value != _currentUser?.name || 
        emailController.value != _currentUser?.email;

      if (needsUserUpdate) {
        final userResult = await UserService.editUser(
          name: nameController.value != _currentUser?.name ? nameController.value : null,
          email: emailController.value != _currentUser?.email ? emailController.value : null,
        );

        switch (userResult) {
          case Success<User, String>():
            setState(() {
              _currentUser = userResult.result;
            });
            break;
          case Failure<User, String>():
            setState(() {
              _isLoading = false;
            });
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(userResult.failure),
                  backgroundColor: AppColors.red,
                  behavior: SnackBarBehavior.floating,
                ),
              );
            }
            return;
        }
      }

      // 2. Atualizar senha se preenchida
      final needsPasswordUpdate = 
        currentPasswordController.value.isNotEmpty && 
        newPasswordController.value.isNotEmpty;

      if (needsPasswordUpdate) {
        if (newPasswordController.value != confirmPasswordController.value) {
          setState(() {
            _isLoading = false;
          });
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('As senhas não coincidem'),
                backgroundColor: AppColors.red,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          return;
        }

        final passwordResult = await UserService.editPassword(
          currentPassword: currentPasswordController.value,
          newPassword: newPasswordController.value,
        );

        switch (passwordResult) {
          case Success<User, String>():
            // Limpar campos de senha após sucesso
            setState(() {
              currentPasswordController.value = '';
              newPasswordController.value = '';
              confirmPasswordController.value = '';
            });
            break;
          case Failure<User, String>():
            setState(() {
              _isLoading = false;
            });
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(passwordResult.failure),
                  backgroundColor: AppColors.red,
                  behavior: SnackBarBehavior.floating,
                ),
              );
            }
            return;
        }
      }

      // 3. Sucesso geral
      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        String message = '';
        if (needsUserUpdate && needsPasswordUpdate) {
          message = 'Dados e senha atualizados com sucesso!';
        } else if (needsUserUpdate) {
          message = 'Dados atualizados com sucesso!';
        } else if (needsPasswordUpdate) {
          message = 'Senha alterada com sucesso!';
        } else {
          message = 'Nenhuma alteração detectada.';
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: needsUserUpdate || needsPasswordUpdate ? Colors.green : AppColors.blue,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro inesperado ao salvar alterações'),
            backgroundColor: AppColors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  Future<void> _handleUpdatePhoto() async {
    final result = await showDialog<ImageSource>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Escolha uma opção'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Câmera'),
              onTap: () => Navigator.pop(context, ImageSource.camera),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Galeria'),
              onTap: () => Navigator.pop(context, ImageSource.gallery),
            ),
            if (_currentUser?.photo == true)
              ListTile(
                leading: const Icon(Icons.delete),
                title: const Text('Remover foto'),
                onTap: () => Navigator.pop(context, null),
              ),
          ],
        ),
      ),
    );

    if (result == null && _currentUser?.photo == true) {
      final removeResult = await UserService.removeUserPhoto();
      switch (removeResult) {
        case Success<User, String>():
          setState(() {
            _currentUser = removeResult.result;
          });
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Foto removida com sucesso!'),
                backgroundColor: Colors.green,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          break;
        case Failure<User, String>():
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(removeResult.failure),
                backgroundColor: AppColors.red,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          break;
      }
    } else if (result != null) {
      // Atualizar foto
      final updateResult = await UserService.editUserPhoto(source: result);
      switch (updateResult) {
        case Success<User, String>():
          setState(() {
            _currentUser = updateResult.result;
          });
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Foto atualizada com sucesso!'),
                backgroundColor: Colors.green,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          break;
        case Failure<User, String>():
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(updateResult.failure),
                backgroundColor: AppColors.red,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          break;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    print(_currentUser?.photoUrl);
    return Scaffold(
      appBar: AppBar(
        title: const Text("Perfil", style: TextStyle(
          color: AppColors.white
        ),),
        leading: IconButton(
          onPressed: () {
            AppRoutes.pop(context);
          },
          icon: const FaIcon(FontAwesomeIcons.chevronLeft, size: 24, color: AppColors.white,)
        ),
        backgroundColor: AppColors.blue,
      ),
      backgroundColor: AppColors.blue,
      body: Container(
        decoration: const BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(12),
            topRight: Radius.circular(12),
          )
        ),
        width: double.infinity,
        child: SafeArea(
          child: Padding(
            padding: AppPaddings.screen,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Padding(
                        padding: keyboardState == KeyboardState.closed ? const EdgeInsets.symmetric(
                          vertical: 16
                        ) : EdgeInsets.zero,
                        child: Column(
                          children: [
                            AnimatedContainer(
                              duration: kThemeAnimationDuration,
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: Color(0xFFE1E1E1),
                              ),
                              height: keyboardState == KeyboardState.closed ? 152 : 0,
                              padding: AppPaddings.medium,
                              clipBehavior: Clip.hardEdge,
                              child: Center(
                                child: _currentUser?.photo == true
                                  ? ClipOval(
                                      child: Image.network(
                                        _currentUser!.photoUrl,
                                        width: 120,
                                        height: 120,
                                        fit: BoxFit.cover,
                                        loadingBuilder: (context, child, loadingProgress) {
                                          if (loadingProgress == null) return child;
                                          return const CircularProgressIndicator();
                                        },
                                        errorBuilder: (context, error, stackTrace) => 
                                          const FaIcon(
                                            FontAwesomeIcons.solidUser,
                                            size: 84,
                                            color: Color(0xFF3C3C3C),
                                          ),
                                      ),
                                    )
                                  : const FaIcon(
                                      FontAwesomeIcons.solidUser,
                                      size: 84,
                                      color: Color(0xFF3C3C3C),
                                    ),
                              ),
                            ),
                            Visibility(
                              visible: keyboardState == KeyboardState.closed,
                              child: TextButton(
                                onPressed: _handleUpdatePhoto,
                                child: const Text(
                                  "Alterar foto",
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 18,
                                    color: Color(0xFF505050)
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            )
                          ],
                        ),
                      ),
                      Flexible(
                        child: SingleChildScrollView(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              AppTextInput(
                                label: "Nome",
                                leading: FontAwesomeIcons.signature,
                                controller: nameController,
                              ),
                              AppTextInput(
                                label: "E-mail",
                                leading: FontAwesomeIcons.solidEnvelope,
                                controller: emailController,
                              ),
                              AppTextInput(
                                label: "Senha atual",
                                leading: FontAwesomeIcons.lock,
                                controller: currentPasswordController,
                                secret: currentPasswordSecret,
                              ),
                              AppTextInput(
                                label: "Nova senha",
                                leading: FontAwesomeIcons.lock,
                                controller: newPasswordController,
                                secret: newPasswordSecret,
                              ),
                              AppTextInput(
                                label: "Confirmar nova senha",
                                leading: FontAwesomeIcons.lock,
                                controller: confirmPasswordController,
                                secret: confirmPasswordSecret,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: AppButton(
                            enabled: !_isLoading,
                            onClick: (context) => _handleSaveChanges(),
                            child: _isLoading 
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: AppColors.white,
                                  ),
                                )
                              : const Text("Salvar alterações")
                          ),
                        ),
                      ],
                    )
                  ],
                )
              ],
            ),
          )
        ),
      ),
    );
  }
}