import java.util.Scanner; //6.3b

public class E6_3b {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a line: ");
        String line = input.nextLine();

        System.out.print("Every second letter: ");
        for (int i = 1; i < line.length(); i += 2) {
            System.out.print(line.charAt(i));
        }

        input.close();
    }
}

