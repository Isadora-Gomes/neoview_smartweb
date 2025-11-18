import 'package:flutter/material.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/constants/styles.dart';

class AppButton extends StatelessWidget {
  final bool enabled;
  final bool hollow;
  final bool small;
  final String? hint;
  final Widget child;
  final void Function(BuildContext context) onClick;
  
  const AppButton({ super.key, this.enabled = true, this.small = false, this.hint, required this.onClick, this.hollow = false, required this.child });
  const factory AppButton.squared({ Key key, bool enabled, required void Function(BuildContext) onClick, String? hint, bool hollow, required Widget child }) = _AppSquaredButton;

  ButtonStyle get _style => hollow
    ? (small ? _borderButtonStyleSmallPadding : _borderButtonStyle)
    : (small ? _buttonStyleSmallPadding : _buttonStyle);

  @override
  Widget build(BuildContext context) {
    return MergeSemantics(
      child: Semantics(
        hint: enabled ? null : hint,
        child: ElevatedButton(
          onPressed: enabled ? () => onClick(context) : null,
          style: _style,
          child: child
        ),
      ),
    );
  }
}

class _AppSquaredButton extends AppButton {
  @override
  Widget get child => Center(child: super.child);

  @override
  ButtonStyle get _style => hollow
    ? _borderButtonStyleNoPadding
    : _buttonStyleNoPadding;

  const _AppSquaredButton({
    super.key,
    super.enabled,
    super.hollow,
    super.hint,
    required super.onClick,
    required super.child
  }): super();

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: SizedBox(
        height: 40,
        width: 40,
        child: AspectRatio(
          aspectRatio: 1,
          child: super.build(context),
        ),
      ),
    );
  }
}

const _defaultButtonStyle = ButtonStyle(
  padding: WidgetStatePropertyAll(AppPaddings.big),
  iconSize: WidgetStatePropertyAll(18),
  shape: WidgetStatePropertyAll(RoundedRectangleBorder(borderRadius: AppBorderRadius.big)),
);

Widget Function(BuildContext, Set<WidgetState>, Widget?) _fullBackgroundBuilderGenerator({
  required Map<WidgetState, Border> borders,
  required Map<WidgetState, Color> backgrounds,
}) {
  return (context, states, child) {
    final priorityState = _getPriorityState(states);
    return AnimatedContainer(
      duration: kThemeAnimationDuration,
      decoration: BoxDecoration(
        border: borders[priorityState] ?? _anyBorder,
        borderRadius: AppBorderRadius.big,
        color: backgrounds[priorityState] ?? _anyBackground,
      ),
      child: child,
    );
  };
}

Widget Function(BuildContext, Set<WidgetState>, Widget?) _borderBackgroundBuilderGenerator({
  required Map<WidgetState, Border> borders,
  required Map<WidgetState, Color> backgrounds,
}) {
  return (context, states, child) {
    final priorityState = _getPriorityState(states);
    return AnimatedContainer(
      duration: kThemeAnimationDuration,
      decoration: BoxDecoration(
        border: borders[priorityState] ?? _anyBorder,
        borderRadius: AppBorderRadius.big,
        color: states.contains(WidgetState.hovered)
          || states.contains(WidgetState.pressed)
          || states.contains(WidgetState.focused) ?
            backgrounds[priorityState] ?? _anyTranslucentBackground :
            Colors.transparent,
      ),
      child: child,
    );
  };
}

final _buttonStyle = _defaultButtonStyle.copyWith(
  textStyle: const WidgetStatePropertyAll(AppTextStyles.button),
  iconColor: const WidgetStatePropertyAll(AppColors.white),
  foregroundColor: WidgetStateMapper({
    WidgetState.disabled: AppColors.grey.shade200,
    WidgetState.pressed: AppColors.grey.shade100,
    WidgetState.any: AppColors.white,
  }),
  backgroundBuilder: _fullBackgroundBuilderGenerator(borders: _borders, backgrounds: _backgrounds)
);

final _borderButtonStyle = _defaultButtonStyle.copyWith(
  textStyle: const WidgetStatePropertyAll(AppTextStyles.hollowButton),
  backgroundBuilder: _borderBackgroundBuilderGenerator(borders: _borders, backgrounds: _translucentBackgrounds)
);

final _buttonStyleNoPadding = _buttonStyle.copyWith(
  padding: const WidgetStatePropertyAll(AppPaddings.tiny),
);

final _borderButtonStyleNoPadding = _borderButtonStyle.copyWith(
  padding: const WidgetStatePropertyAll(AppPaddings.tiny),
);

final _buttonStyleSmallPadding = _buttonStyle.copyWith(
  padding: const WidgetStatePropertyAll(AppPaddings.small),
  textStyle: const WidgetStatePropertyAll(AppTextStyles.smallButton),
);

final _borderButtonStyleSmallPadding = _borderButtonStyle.copyWith(
  padding: const WidgetStatePropertyAll(AppPaddings.small),
  textStyle: const WidgetStatePropertyAll(AppTextStyles.smallButton),
);

WidgetStatesConstraint _getPriorityState(Set<WidgetState> states) {
  if (states.contains(WidgetState.disabled)) return WidgetState.disabled;
  if (states.contains(WidgetState.error)) return WidgetState.error;
  if (states.contains(WidgetState.pressed)) return WidgetState.pressed;
  if (states.contains(WidgetState.focused)) return WidgetState.focused;
  if (states.contains(WidgetState.hovered)) return WidgetState.hovered;
  return WidgetState.any;
}

final _borders = {
  WidgetState.error: Border.fromBorderSide(BorderSide(
    color: AppColors.red,
    width: 2,
  )),
  WidgetState.disabled: Border.fromBorderSide(BorderSide(
    color: AppColors.grey.shade700,
    width: 2,
  )),
  WidgetState.pressed: Border.fromBorderSide(BorderSide(
    color: AppColors.blue.shade800,
    width: 2,
  )),
  WidgetState.hovered: Border.fromBorderSide(BorderSide(
    color: AppColors.blue.shade600,
    width: 2,
  )),
  WidgetState.focused: Border.fromBorderSide(BorderSide(
    color: AppColors.blue.shade600,
    width: 2,
  )),
};

final _anyBorder = Border.fromBorderSide(BorderSide(
  color: AppColors.blue,
  width: 2,
));

final _backgrounds = {
  WidgetState.error: AppColors.red,
  WidgetState.disabled: AppColors.grey.shade700,
  WidgetState.pressed: AppColors.blue.shade800,
  WidgetState.hovered: AppColors.blue.shade600,
  WidgetState.focused: AppColors.blue.shade600,
};

final _translucentBackgrounds = _backgrounds.map((key, value) {
  return MapEntry(key, value.withAlpha(64));
},);

final _anyBackground = AppColors.blue;

final _anyTranslucentBackground = AppColors.blue.withAlpha(64);