import java.util.Scanner;  //E6.3c

public class E6_3c {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a line: ");
        String line = input.nextLine();

        String result = "";
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if ("aeiouAEIOU".indexOf(ch) != -1) {
                result += "_";
            } else {
                result += ch;
            }
        }

        System.out.println(result);
        input.close();
    }
}

