import 'package:flutter/material.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/constants/styles.dart';
import 'package:neoview/core/navigation.dart';
import 'package:neoview/widgets/app_app_bar.dart';
import 'package:neoview/widgets/app_button.dart';
import 'package:neoview/widgets/app_drawer.dart';
import 'package:neoview/widgets/underline_text.dart';

class Instructions extends StatefulWidget {
  const Instructions({super.key});

  @override
  State<Instructions> createState() => _InstructionsState();
}

class _InstructionsState extends State<Instructions> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      onDrawerChanged: drawerNavigationStyler,
      appBar: AppAppBar(
        actions: [
          ExcludeSemantics(
            child: AppButton(
              small: true,
              onClick: (context) {
                AppRoutes.pair.popAndStack(context);
              },
              child: const Text("Conectar NeoView")
            ),
          )
        ],
      ),
      // appBar: AppBar(
      //   leading: AppDrawerButton(),
      //   backgroundColor: AppColors.white,
      //   surfaceTintColor: AppColors.white,
      //   actions: [
      //     AppButton(onClick: (context) {
      //       AppRoutes.pair.popAndStack(context);
      //     }, child: const Text("Conectar NeoView")),
      //     SizedBox(
      //       width: kScreenPadding,
      //     )
      //   ],
      // ),
      drawer: AppDrawer(),
      body: SingleChildScrollView(
        child: Column(
          children: [
            Padding(
              padding: AppPaddings.screen,
              child: SizedBox(
                width: double.infinity,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  mainAxisSize: MainAxisSize.max,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  spacing: 16,
                  children: [
                    Semantics(
                      label: "Manual de conexão do óculos",
                      child: const ExcludeSemantics(child: UnderlineText("Manual de Conexão"))
                    ),
                    Image.asset("assets/images/photo_device_1.png", width: double.infinity,),
                    const ExcludeSemantics(child: UnderlineText("Conheça mais sobre o NeoView")),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 24),
                      child: Text(
                        "O NeoView é um óculos inteligente desenvolvido para pessoas com deficiência visual. Utilizando visão computacional e recursos de acessibilidade, ele auxilia em tarefas do dia a dia, promovendo mais autonomia, segurança e inclusão.",
                        style: AppTextStyles.mainText,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Container(
              color: AppColors.lightBlue,
              width: double.infinity,
              padding: const EdgeInsets.all(32),
              child: SafeArea(
                top: false,
                child: Column(
                  spacing: 32,
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    const UnderlineText("Passo a passo"),
                    const _InstructionCard(
                      index: 1,
                      title: "Ligue o NeoView",
                      text: "Pressione o botão lateral até ouvir o sinal sonoro."
                    ),
                    const _InstructionCard(
                      index: 2,
                      title: "Ative o Wi-Fi do celular",
                      text: "Entre nas configurações e verifique as redes disponíveis."
                    ),
                    const _InstructionCard(
                      index: 3,
                      title: "Abra o aplicativo NeoView",
                      text: "Entre em Conectar NeoView e procure pela rede do seu óculos."
                    ),
                    const _InstructionCard(
                      index: 4,
                      title: "Selecione seu óculos",
                      text: "Conecte-se ao seu óculos, exibindo uma nova tela com suas informações."
                    ),
                    const _InstructionCard(
                      index: 5,
                      title: "Conexão concluída!",
                      text: "Seu óculos já está pronto para ser usado."
                    ),
                    const SizedBox(),
                    Row(
                      children: [
                        Expanded(
                          child: AppButton(
                            onClick: (context) {
                              AppRoutes.pair.popAndStack(context);
                            },
                            child: const Text("Conectar NeoView")
                          ),
                        ),
                      ],
                    )
                  ],
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}

class _InstructionCard extends StatelessWidget {
  final String title;
  final String text;
  final int index;

  const _InstructionCard({
    required this.index,
    required this.title,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return MergeSemantics(
      child: Container(
        decoration: const BoxDecoration(
          color: AppColors.white,
          borderRadius: AppBorderRadius.medium,
        ),
        padding: AppPaddings.bigger,
        child: Column(
          spacing: 16,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            RichText(
              text: TextSpan(
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: AppColors.black
                ),
                children: [
                  TextSpan(
                    text: "$index. ",
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: AppColors.blue
                    ),
                  ),
                  TextSpan(
                    text: title,
                  )
                ]
              ),
            ),
            Text(text, style: AppTextStyles.mainText,),
          ],
        ),
      ),
    );
  }
}