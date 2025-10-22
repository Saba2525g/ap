
import java.util.Scanner;

public class E6_2b {      //E6.2b
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("Enter integers (0 to stop):");
        int even = 0;
        int odd = 0;
        int number = input.nextInt();

        while (number != 0) {
            if (number % 2 == 0) even++;
            else odd++;
            number = input.nextInt();
        }

        System.out.println("Even numbers: " + even);
        System.out.println("Odd numbers: " + odd);

        input.close();
    }
}
