import java.util.Scanner; //E_6_3_e

public class E6_3e {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a line: ");
        String line = input.nextLine();

        System.out.print("Positions of vowels: ");
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if ("aeiouAEIOU".indexOf(ch) != -1) {
                System.out.print(i + " ");
            }
        }

        input.close();
    }
}

