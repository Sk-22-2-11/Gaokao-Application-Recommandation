   M S B A M L   `   `   `  ���� E  AGaokao_App, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'clr-namespace:Gaokao_App
Gaokao_App      Gaokao_App.MainWindow   W SPresentationCore, Version=6.0.2.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=6.0.2.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35e aSystem.Windows.Controls.Ribbon, Version=6.0.2.0, Culture=neutral, PublicKeyToken=b77a5c561934e089R NWindowsBase, Version=6.0.2.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35F 9http://schemas.microsoft.com/winfx/2006/xaml/presentation     R NSystem.Xaml, Version=6.0.2.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     @d2http://schemas.microsoft.com/expression/blend/2008     Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     *localclr-namespace:Gaokao_App       � Title$  参数输入��$	��750��$
��1100�� � Icon$ /favicon.ico������  �� ImageSource$ /bc.jpg�� � 	Resources  �� 
TargetType �� Property �� Value �� 
TargetType �� CornerRadius	 �� Triggers
 :� RoutedEvent �� TargetProperty W� From	 W� To g� Duration g� AutoReverse �� Binding �� Value��%  '��       '�� q     '�� E    '� �    �� " ��.���  � ��$ Segoe UI)���  � ��$ 14(���  � ��$ 10q���  � �� �#FFD700�� " ��.���  � ��$ Segoe UI)���  � ��$ 14(���  � ��$ 10q���  � ��$ 10q���  � ��$ 1q���  � �� �#4CAF50��  � �� �#F1F1F1��  � �� �#333333�� " ��.���  � �� �#4CAF50��  � ��
 �������  � ��$ Segoe UI)���  � ��$ 14(���  � ��$ 10q���  � ��$ 10q���  � ��$ 1q���  � �� �#4CAF50��  � �� �� " ��.R��� #��z��#��z��#��z��$ 5��._��� $��Center=�$��Center=�	 :� $
 Button.Click��.[��� .���� .��W� $ Opacity� 1 0.8$ 0:0:0.1D�$
 True���� " �.���  � ��$	 400����  � ��$ 20����  � ��$
 0,20q���  �@�Minimum$ 0Q���  �@�Maximum$ 3Q���  � �� �#4CAF50��  � y�$ 	Collapsed=�	 ��  �� *IsInProgress+ True.a���  � y�$ Visible=�.��� $��Center=�$��Center=� � ColumnDefinitions �� $	��600 � � RowDefinitions �� $
��Auto ��� $
��Auto ��� $
��Auto ��� $
��Auto ��� $
��Auto ��� $
��Auto �$��40���� $
��Auto ��� $
��Auto ��� $
��Auto �.+��� $��0��$��2��$��10q�.+��� $$��清北之路志愿推荐系统��$��Center=�$��Center=�$��24(�$
��Bold"�$��0,20,0,0q��� $��1��$��2��$��10q�.+��� $��	姓名：��$
��Bold"�$	��200���� -    ��Name$ txtName��$	��200��$��张三���� $��2��$��2��$��10q�.+��� $��	科目：��$
��Bold"�$	��200���� -    ��Name$ 
cmbSubject��$	��200�� �� SelectedIndex$ 0��.@��� $��文科���� $��理科���� $��3��$��2��$��10q�.+��� $��高考排名：��$
��Bold"�$	��200���� -   $ txtRank��$	��200��$��45000���� $��4��$��2��$��10q�.+��� $!��想争取的最高排名：��$
��Bold"�$	��200���� -   $ 
txtRankMax��$	��200��$��40000���� $��5��$��2��$��10q�.+��� $!��能接受的最低排名：��$
��Bold"�$	��200���� -   $ 
txtRankMin��$	��200��$��50000���� -   $��6��$��2��$��确认��$	��100��� -    �Name$ progressBar��$��7��$��2��$	��600��$��20�� � Minimum$ 0Q� � Maximum$	 1.5Q�$y�Visible=�