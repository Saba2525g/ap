import java.util.Scanner; //E_6_3_a

public class E6_3a {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a line: ");
        String line = input.nextLine();

        System.out.print("Uppercase letters: ");
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch >= 'A' && ch <= 'Z') {
                System.out.print(ch);
            }
        }

        input.close();
    }
}

