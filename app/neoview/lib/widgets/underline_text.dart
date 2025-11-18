import 'package:flutter/material.dart';
import 'package:neoview/core/constants/styles.dart';

class UnderlineText extends StatelessWidget {
  final String text;

  const UnderlineText(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        border: Border(
          bottom: AppBorders.underline
        ),
      ),
      padding: const EdgeInsets.only(bottom: 4, left: 4, right: 8),
      child: Text(text, style: AppTextStyles.title,),
    );
  }
}