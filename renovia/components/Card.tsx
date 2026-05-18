import { View, Pressable } from "react-native";
import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  onPress?: () => void;
  className?: string;
};

export function Card({ children, onPress, className = "" }: Props) {
  const base = `bg-white rounded-card p-4 ${className}`;
  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        className={base}
        style={{
          shadowColor: "#0B1320",
          shadowOpacity: 0.06,
          shadowRadius: 12,
          shadowOffset: { width: 0, height: 4 },
          elevation: 2,
        }}
      >
        {children}
      </Pressable>
    );
  }
  return (
    <View
      className={base}
      style={{
        shadowColor: "#0B1320",
        shadowOpacity: 0.06,
        shadowRadius: 12,
        shadowOffset: { width: 0, height: 4 },
        elevation: 2,
      }}
    >
      {children}
    </View>
  );
}
