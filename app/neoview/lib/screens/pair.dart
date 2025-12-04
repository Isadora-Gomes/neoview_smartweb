import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/constants/styles.dart';
import 'package:neoview/core/navigation.dart';
import 'package:neoview/widgets/app_app_bar.dart';
import 'package:neoview/widgets/app_button.dart';
import 'package:neoview/widgets/app_drawer.dart';
import 'package:neoview/widgets/underline_text.dart';
import 'package:neoview/features/pair.dart' as model;

class Pair extends StatefulWidget {
  const Pair({super.key});

  @override
  State<Pair> createState() => _PairState();

  static _PairState _of(BuildContext context) => context.findAncestorStateOfType<_PairState>()!;
}

class _PairState extends State<Pair> {
  void update(void Function() callback) => setState(callback);

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
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            spacing: 32,
            children: [
              Column(
                spacing: 8,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const UnderlineText("Conectar NeoView"),
                  const Text(
                    "Mantenha o óculos NeoView perto do seu celular e toque em ‘Conectar’ para iniciar o pareamento.",
                    style: AppTextStyles.mainText,
                  ),
                  Flexible(
                    fit: FlexFit.loose,
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        return SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            spacing: 8,
                            children: [
                              for (var pair in model.Pair.statics)
                                SizedBox(
                                  width: constraints.maxWidth,
                                  child: _NeoViewGlassesCard(pair, constraints)
                                ),
                              ]
                          ),
                        );
                      }
                    ),
                  ),
                ],
              ),
              Flexible(
                fit: FlexFit.tight,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 32.0),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.end,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    spacing: 8,
                    children: [
                      const Text(
                        "Disparar funções",
                        semanticsLabel: "Disparar funções do óculos",
                        style: AppTextStyles.subtitle,
                      ),
                      Expanded(
                        child: IntrinsicHeight(
                          child: SingleChildScrollView(
                            // reverse: true,
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
                              ],
                            ),
                          ),
                        ),
                      )
                    ],
                  ),
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
  final model.Pair pair;
  final BoxConstraints constraints;

  const _NeoViewGlassesCard(this.pair, this.constraints);

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: "Óculos NeoView não conectado",
      child: Container(
        decoration: const BoxDecoration(
          border: Border.fromBorderSide(AppBorders.underline),
          borderRadius: AppBorderRadius.big
        ),
        padding: AppPaddings.big,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Flexible(
                  fit: FlexFit.loose,
                  flex: 4,
                  child: Image.asset("assets/images/photo_device_1.png"),
                ),
                Flexible(
                  fit: FlexFit.loose,
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
                            Pair._of(context).update(() {
                              if (pair == model.Pair.connected) {
                                model.Pair.connected = null;
                              } else {
                                model.Pair.connected = pair;
                              }
                            },);
                          },
                          child: ExcludeSemantics(
                            child: Text(pair == model.Pair.connected ? "Desconectar" : "Conectar", style: const TextStyle(
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
          ],
        ),
      ),
    );
  }
}