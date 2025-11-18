import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/navigation.dart';
import 'package:neoview/widgets/app_button.dart';
import 'package:neoview/widgets/app_dialog.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      semanticLabel: "Menu de navegação",
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.zero,
        side: BorderSide.none,
      ),
      backgroundColor: AppColors.blue,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          SafeArea(
            child: Padding(
              padding: AppPaddings.medium,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.start,
                spacing: 24,
                children: [
                  ExcludeSemantics(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      spacing: 8,
                      children: [
                        Image.asset("assets/icons/white.png", width: 48,),
                        const Text("NEOVIEW", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.white),),
                      ],
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    spacing: 8,
                    children: [
                      const _DrawerButton(
                        icon: FontAwesomeIcons.solidHouse,
                        text: "Início",
                        route: AppRoutes.home,
                        reset: true,
                      ),
                      const _DrawerButton(
                        icon: FontAwesomeIcons.wifi,
                        text: "Conectar NeoView",
                        route: AppRoutes.pair
                      ),
                      const _DrawerButton(
                        icon: FontAwesomeIcons.clipboardQuestion,
                        text: "Manual de Conexão",
                        route: AppRoutes.instructions
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          Column(
            mainAxisAlignment: MainAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: AppPaddings.medium,
                decoration: const BoxDecoration(
                  color: Color(0x55808080)
                ),
                child: SafeArea(
                  top: false,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.start,
                        crossAxisAlignment: CrossAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        spacing: 8,
                        children: [
                          Container(
                            decoration: const BoxDecoration(
                              color: Color.fromARGB(255, 170, 170, 170),
                              shape: BoxShape.circle,
                            ),
                            padding: AppPaddings.medium,
                            child: Center(child: const FaIcon(FontAwesomeIcons.solidUser, color: AppColors.black, size: 32,)),
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              ExcludeSemantics(
                                child: Text("Usuário", style: const TextStyle(
                                  color: AppColors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16
                                ),),
                              ),
                              Semantics(
                                button: true,
                                label: "Ir para perfil",
                                child: GestureDetector(
                                  onTap: () => _buttonForProfile._navigate(context),
                                  child: const ExcludeSemantics(
                                    child: 
                                      Row(
                                        children: [
                                          Text(
                                            "Meu perfil ",
                                            style: TextStyle(
                                              fontSize: 16,
                                              color: AppColors.white
                                            ),
                                          ),
                                          FaIcon(FontAwesomeIcons.chevronRight, size: 16, color: AppColors.white,)
                                        ],
                                      )
                                  )
                                ),
                              )
                            ],
                          ),
                        ],
                      ),
                      Semantics(
                        label: "Sair da conta",
                        button: true,
                        child: GestureDetector(
                          behavior: HitTestBehavior.translucent,
                          onTap: () => _logout(context),
                          child: const FaIcon(FontAwesomeIcons.rightFromBracket, size: 32, color: AppColors.white,),
                        ),
                      )
                    ],
                  ),
                ),
              )
            ],
          )
        ],
      ),
    );
  }
}

const _DrawerButton _buttonForProfile = _DrawerButton(
  icon: FontAwesomeIcons.solidUser,
  text: "Perfil",
  route: AppRoutes.profile
);

void _logout(BuildContext context) {
  showDialog(
    context: context,
    builder: (context) {
      return AppDialog(
        icon: FontAwesomeIcons.exclamation,
        title: "Confirmar saída",
        body: const Text("Tem certeza que deseja sair de sua conta?"),
        actions: [
          AppButton(
            small: true,
            onClick: (context) => AppRoutes.login.resetTo(context),
            child: const Text("Sair")
          ),
          AppButton(
            small: true,
            onClick: (context) => Navigator.of(context).pop(),
            child: const Text("Cancelar")
          )
        ],
      );
    },
  );
}

class _DrawerButton extends StatelessWidget {
  final IconData icon;
  final String text;
  final AppRoutes route;
  final bool reset;

  const _DrawerButton({
    required this.icon,
    required this.text,
    required this.route,
    this.reset = false,
  });

  void _navigate(BuildContext context) {
    Scaffold.of(context).closeDrawer();
    if (reset) {
      route.resetTo(context);
    } else {
      if (AppRoutes.currentRoute == AppRoutes.home) {
        route.stack(context);
      } else {
        route.popAndStack(context);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: "Navegar para $text",
      hint: route == AppRoutes.currentRoute ? "Você já está nesta tela" : null,
      button: true,
      enabled: route != AppRoutes.currentRoute,
      child: GestureDetector(
        behavior: HitTestBehavior.translucent,
        onTap: () => _navigate(context),
        child: ExcludeSemantics(
          child: Container(
            decoration: route == AppRoutes.currentRoute
              ? const BoxDecoration(
                borderRadius: AppBorderRadius.small,
                color: Color(0x3B797979)
              )
              : const BoxDecoration(
                borderRadius: AppBorderRadius.small
              ),
            padding: AppPaddings.small,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              spacing: 8,
              children: [
                SizedBox.square(
                  dimension: 32,
                  child: Center(child: FaIcon(icon, size: 24, color: AppColors.white,)),
                ),
                Text(text, style: const TextStyle(color: AppColors.white, fontSize: 16),),
              ],
            ),
          ),
        ),
      ),
    );
  }
}