package learn.learning;

import java.io.IOException;
import java.util.*;

import com.ibm.icu.impl.locale.LanguageTag;
import it.uniroma1.lcl.babelnet.data.*;
import it.uniroma1.lcl.babelnet.iterators.BabelIterator;
import it.uniroma1.lcl.jlt.util.UniversalPOS;
import com.google.common.collect.Multimap;

import it.uniroma1.lcl.babelnet.BabelNet;
import it.uniroma1.lcl.babelnet.BabelNetQuery;
import it.uniroma1.lcl.babelnet.BabelNetUtils;
import it.uniroma1.lcl.babelnet.BabelSense;
import it.uniroma1.lcl.babelnet.BabelSenseComparator;
import it.uniroma1.lcl.babelnet.BabelSynset;
import it.uniroma1.lcl.babelnet.BabelSynsetComparator;
import it.uniroma1.lcl.babelnet.BabelSynsetID;
import it.uniroma1.lcl.babelnet.BabelSynsetRelation;
import it.uniroma1.lcl.babelnet.InvalidSynsetIDException;
import it.uniroma1.lcl.babelnet.iterators.BabelLexiconIterator;
import it.uniroma1.lcl.babelnet.iterators.WordNetSynsetIterator;
import it.uniroma1.lcl.babelnet.iterators.BabelSynsetIterator;
import it.uniroma1.lcl.jlt.util.Language;
import it.uniroma1.lcl.jlt.util.ScoredItem;
import it.uniroma1.lcl.kb.SynsetType;
import org.apache.commons.codec.language.bm.Languages;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.search.IndexSearcher;
import it.uniroma1.lcl.jlt.ling.Word;
//import it.uniroma1.lcl.babelnet.data.BabelPOS;
import it.uniroma1.lcl.jlt.util.POS;
//import com.babelscape.utils.UniversalPOS;
import java.io.FileWriter;

/**
 * Convert BabelNet to series of text files where each line has the format:
 * LANG~BabelSynsetID~lexeme
 *
 */
public class syn2vec_getAllSynsetsBabelNet_iterator{

    public static void mainTest() throws IOException {
        BabelNet bn = BabelNet.getInstance();

        BabelSynsetIterator bsyn_it_dum = (BabelSynsetIterator) bn.getSynsetIterator();
        BabelSynset syn1 = bsyn_it_dum.next();

        BabelSynsetIterator bsyn_it = (BabelSynsetIterator) bn.getSynsetIterator();
        String lang = "";

        ArrayList<String> all_data_as_string = new ArrayList();

        int stop = 1;  // just for setting some debugging breakpoints
        int counter = 0;
        List<BabelSense> senses1 = syn1.getSenses();
        while (bsyn_it.hasNext()){
            syn1 = bsyn_it.next();
            String id = syn1.getID().getID();
            senses1 = syn1.getSenses();
            for (BabelSense local_sense : senses1) {
                String lemma = local_sense.getLemma().toString();
                String lem_lang = local_sense.getLanguage().toString();

                String all_info = lem_lang + "~" + id + "~" + lemma;
                all_data_as_string.add(all_info);

                String temp_info = lem_lang + "~" + lemma;
            }
            stop = 1;
            if (counter % 1000 == 0){
                System.out.println(counter);
            }
            if (counter % 100000 == 0 & counter < 30000000){
                String count2str = String.valueOf(counter);
                // Depending on where you put this script, you need to create the dump directory yourself
                // We use 'synset_text_files' as the dump directory
                FileWriter writer = new FileWriter("synset_text_files/" + count2str + ".txt");
                for(String str: all_data_as_string) {
                    writer.write(str + System.lineSeparator());
                }
                writer.close();
                // Clear all_data_as_string because we can't hold it all in memory!!!
                all_data_as_string.clear();
                System.out.println("Saved file for " + count2str + " to disk...");
//              System.out.println(word);
            }
            counter++;
        }
        String count2str = String.valueOf(counter);
        FileWriter writer = new FileWriter("synset_text_files/" + count2str + ".txt");
        for(String str: all_data_as_string) {
            writer.write(str + System.lineSeparator());
        }
        writer.close();
        // Clear all_data_as_string because we can't hold it all in memory!!!
        all_data_as_string.clear();
        System.out.println("Saved FINAL file for " + count2str + " to disk...");

    }

    static public void main(String[] args)
    {
        try
        {

//            BabelNet bn = BabelNet.getInstance();

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
