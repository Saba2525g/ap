import java.util.Scanner; //E5.18
import java.util.Arrays;

public class E5_18 {

    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter three strings: ");
        String s1 = input.next();
        String s2 = input.next();
        String s3 = input.next();

        String[] words = { s1, s2, s3 };

        Arrays.sort(words);

        System.out.println("Here is the order from A to Z:");
        System.out.println(words[0]);
        System.out.println(words[1]);
        System.out.println(words[2]);

        input.close();
    }
}
