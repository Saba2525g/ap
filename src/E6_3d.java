import java.util.Scanner; //E6.3d

public class E6_3d {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a line: ");
        String line = input.nextLine();

        int count = 0;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if ("aeiouAEIOU".indexOf(ch) != -1) {
                count++;
            }
        }

        System.out.println("Number of vowels: " + count);
        input.close();
    }
}

