import java.util.Scanner; //E_6_13

public class E6_13 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a number: ");
        int number = input.nextInt();

        while (number > 0) {
            int digit = number % 2;
            System.out.println(digit);
            number = number / 2;
        }

        input.close();
    }
}

