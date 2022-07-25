package learn.learning;

import java.io.IOException;
import java.util.*;

import it.uniroma1.lcl.babelnet.*;
import it.uniroma1.lcl.babelnet.data.*;
import com.google.common.collect.Multimap;

import it.uniroma1.lcl.babelnet.iterators.BabelLexiconIterator;
import it.uniroma1.lcl.babelnet.iterators.WordNetSynsetIterator;
import it.uniroma1.lcl.babelnet.iterators.BabelSynsetIterator;
import it.uniroma1.lcl.jlt.util.Language;
import it.uniroma1.lcl.jlt.util.ScoredItem;
//import it.uniroma1.lcl.babelnet.data.BabelPOS;
import it.uniroma1.lcl.jlt.util.POS;
//import com.babelscape.utils.UniversalPOS;
import java.io.FileWriter;

/**
 * Save all BabelNet synset types, i.e. Concept, Named Entity, or Other in format:
 * BabelSynsetID~type
 *
 */
public class syn2vec_getBabelNetSynsetTypes{


    public static void mainTest() throws IOException {
        BabelNet bn = BabelNet.getInstance();

        BabelSynsetIterator bsyn_it_dum = (BabelSynsetIterator) bn.getSynsetIterator();
        BabelSynset syn1 = bsyn_it_dum.next();

        BabelSynsetIterator bsyn_it = (BabelSynsetIterator) bn.getSynsetIterator();
        BabelLexiconIterator bl_it = (BabelLexiconIterator) bn.getLexiconIterator();
        String lang = "";

        ArrayList<String> all_data_as_string = new ArrayList();

        int stop = 1;
        int counter = 0;
        int concept_counter = 0;
        int unknown_counter = 0;
        int named_entity_counter = 0;
        List<BabelSense> senses1 = syn1.getSenses();
        List<WordNetSynsetID> WordNetIDs = new ArrayList<>();
        String synset_type = new String();
        String savestr = new String();
        while (bsyn_it.hasNext()){
            syn1 = bsyn_it.next();
            synset_type = syn1.getType().toString();
            //synID = syn1.getID().toString();
            if (synset_type == "Concept"){
                concept_counter++;
            }
            else if (synset_type == "Named Entity"){
                named_entity_counter++;
            }
            else if (synset_type == "Unknown"){
                unknown_counter++;
            }

            String id = syn1.getID().getID();
            savestr = id + "~" + synset_type;
            all_data_as_string.add(savestr);

            stop = 1;
            if (counter % 1000 == 0){
                System.out.println(counter);
//                System.out.println(word);
            }
            if (counter % 100000 == 0 & counter < 30000000){
                String count2str = String.valueOf(counter);
                // Depending on where you put this script, you need to create the dump directory yourself
                // We use 'BabelNet_Synset_Types' as the dump directory
                FileWriter writer = new FileWriter("BabelNet_Synset_Types/" + count2str + ".txt");
                for(String str: all_data_as_string) {
                    writer.write(str + System.lineSeparator());
                }
                writer.close();
                // Clear all_data_as_string because we can't hold it all in memory!!!
                all_data_as_string.clear();
                System.out.println("Saved file for " + count2str + " to disk...");
                System.out.println("Concepts: " + String.valueOf(concept_counter));
                System.out.println("Named Entities: : " + String.valueOf(named_entity_counter));
                System.out.println("Unknown: " + String.valueOf(unknown_counter));
//              System.out.println(word);
            }
            counter++;
        }
        String count2str = String.valueOf(counter);
        FileWriter writer = new FileWriter("BabelNet_Synset_Types/" + count2str + ".txt");
        for(String str: all_data_as_string) {
            writer.write(str + System.lineSeparator());
        }
        writer.close();
        // Clear all_data_as_string because we can't hold it all in memory!!!
        all_data_as_string.clear();
        System.out.println("Saved FINAL file for " + count2str + " to disk...");
        System.out.println("Concepts: " + String.valueOf(concept_counter));
        System.out.println("Named Entities: : " + String.valueOf(named_entity_counter));
        System.out.println("Unknown: " + String.valueOf(unknown_counter));


    }


    static public void main(String[] args)
    {
        try
        {

            BabelNet bn = BabelNet.getInstance();

//            BabelSynset synset = bn.getSynset(new BabelSynsetID("bn:03083790n"));
//            BabelSynset synsetv = bn.getSynset(new BabelSynsetID("bn:00091806v"));
//            BabelSynset synseta = bn.getSynset(new BabelSynsetID("bn:00111286a"));
//            BabelSynset synsetr = bn.getSynset(new BabelSynsetID("bn:00116285r"));
//            POS pos = synset.getPOS();
//            POS posv = synsetv.getPOS();
//            POS posa = synseta.getPOS();
//            POS posr = synsetr.getPOS();

            mainTest();


        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }
}
