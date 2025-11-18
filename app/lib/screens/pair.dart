import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/constants/styles.dart';
import 'package:neoview/core/navigation.dart';
import 'package:neoview/widgets/app_app_bar.dart';
import 'package:neoview/widgets/app_button.dart';
import 'package:neoview/widgets/app_dialog.dart';
import 'package:neoview/widgets/app_drawer.dart';
import 'package:neoview/widgets/underline_text.dart';

class Pair extends StatefulWidget {
  const Pair({super.key});

  @override
  State<Pair> createState() => _PairState();
}

class _PairState extends State<Pair> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      onDrawerChanged: drawerNavigationStyler,
      appBar: AppAppBar(),
      drawer: AppDrawer(),
      body: SafeArea(
        child: Padding(
          padding: AppPaddings.screen,
          child: Column(
            spacing: 8,
            children: [
              const UnderlineText("Conectar NeoView"),
              const Text(
                "Mantenha o óculos NeoView perto do seu celular e toque em ‘Conectar’ para iniciar o pareamento.",
                style: AppTextStyles.mainText,
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                spacing: 8,
                children: [
                  _NeoViewGlassesCard()
                ],
              ),
              Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.max,
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  spacing: 8,
                  children: [
                    const Text(
                      "Disparar funções",
                      semanticsLabel: "Disparar funções do óculos",
                      style: AppTextStyles.subtitle,
                    ),
                    Flexible(
                      child: IntrinsicHeight(
                        child: SingleChildScrollView(
                          reverse: true,
                          child: Column(
                            spacing: 8,
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: AppButton(
                                      onClick: (context) {
                                        
                                      },
                                      child: const Text("Identificação de piso tátil")
                                    ),
                                  ),
                                ],
                              ),
                              Row(
                                children: [
                                  Expanded(
                                    child: AppButton(
                                      onClick: (context) {
                                        
                                      },
                                      child: const Text("Detecção de ambiente")
                                    ),
                                  ),
                                ],
                              ),
                              Row(
                                children: [
                                  Expanded(
                                    child: AppButton(
                                      onClick: (context) {
                                        
                                      },
                                      child: const Text("Leitura de textos")
                                    ),
                                  ),
                                ],
                              ),
                              Row(
                                children: [
                                  Expanded(
                                    child: AppButton(
                                      onClick: (context) {
                                        showDialog(
                                          context: context,
                                          builder: (context) => AppDialog(
                                            title: "Modal",
                                            body: Text("Modal"),
                                            icon: FontAwesomeIcons.check,
                                          ),
                                        );
                                      },
                                      child: const Text("GPS inteligente")
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    )
                  ],
                )
              )
            ],
          ),
        )
      ),
    );
  }
}

class _NeoViewGlassesCard extends StatelessWidget {
  const _NeoViewGlassesCard();

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: "Óculos NeoView não conectado",
      child: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          border: Border.fromBorderSide(AppBorders.underline),
          borderRadius: AppBorderRadius.big
        ),
        padding: AppPaddings.big,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              flex: 4,
              child: Image.asset("assets/images/photo_device_1.png"),
            ),
            Expanded(
              flex: 6,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                mainAxisSize: MainAxisSize.max,
                crossAxisAlignment: CrossAxisAlignment.start,
                spacing: 12,
                children: [
                  Row(
                    spacing: 8,
                    children: [
                      Text("Óculos", semanticsLabel: "Nome: Óculos", style: AppTextStyles.subtitle,),
                      Semantics(
                        label: "Editar nome",
                        button: true,
                        child: GestureDetector(
                          onTap: () {
                            
                          },
                          child: const FaIcon(FontAwesomeIcons.pencil, size: 24,),
                        ),
                      )
                    ],
                  ),
                  Semantics(
                    label: "Bateria em 100%",
                    child: ExcludeSemantics(
                      child: Row(
                        spacing: 4,
                        children: [
                          const FaIcon(FontAwesomeIcons.batteryFull, color: Colors.lightGreenAccent, size: 20,),
                          Text("100%", style: AppTextStyles.bold,),
                        ],
                      ),
                    ),
                  ),
                  Semantics(
                    label: "Conectar ao óculos",
                    button: true,
                    child: GestureDetector(
                      onTap: () {
                        
                      },
                      child: ExcludeSemantics(
                        child: const Text("Conectar", style: TextStyle(
                          color: AppColors.blue,
                          fontSize: 18,
                          fontWeight: FontWeight.bold
                        ),),
                      ),
                    ),
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}